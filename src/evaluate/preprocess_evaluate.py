import shutil
import argparse
from pathlib import Path
from tqdm import tqdm
import SimpleITK as sitk
import numpy as np
import os
import yaml
'''
評価に必要なdirづくりをするコード
expreriments/実験名/res直下に予測ラベルができてるので、
expreriments/実験名/ref dirを作成し、そこにraw_dataをcopyしてくる
kits19/data/case_00000/segmentation.nii.gz -> /res/case00000.nii.gz となる
python3 /home/kakeya/Desktop/higuchi/20191021/Keras/src/test/preprocess_evaluate.py /home/kakeya/Desktop/higuchi/20191021/Keras/experiments/1104_75epochs --ref_dir /home/kakeya/Desktop/higuchi/data
'''


def get_exp_yml(args):
    # TODO:もっとスマートな書き方
    with open(args.setting_exp_yml_path) as file:
        exp_yaml = yaml.load(file)

    dir_yaml_path = './dir_setting.exp_yml'
    if dir_yaml_path:
        with open(dir_yaml_path):
            dir_yaml = dir_yaml_path
        return exp_yaml, dir_yaml
    else:
        exp_yaml, None


def ValidateArgs(args, exp_yml):
    OWN_DIR = Path(exp_yml['DIR']['OWN'])
    DATA_DIR = Path(exp_yml['DIR']['DATA'])

    if not OWN_DIR.is_dir():
        print(f'Experiments directory({OWN_DIR}) is not dir')
        return False
    if not DATA_DIR.is_dir():
        print(f'Reference directory({DATA_DIR}) is not dir')
        return False
    return True


def ParseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-exp_yml', '--setting_exp_yml_path', type=str)
    args = parser.parse_args()

    return args


def make_concat_label(kidney_path, CCRCC_path=None, cyst_path=None):
    # TODO:kid,ccrccなど固有名詞を取り除く。ラベル数が動的でも動くコードにする。
    '''concat&return labels'''
    print(kidney_path.is_file(), CCRCC_path.is_file(), cyst_path.is_file())
    if not kidney_path.is_file():
        assert ValueError(f'{kidney_path} isn`t exist')
    kid = sitk.GetArrayFromImage(sitk.ReadImage(str(kidney_path)))
    ccrcc = sitk.GetArrayFromImage(sitk.ReadImage(str(CCRCC_path))) if CCRCC_path.is_file() else np.zeros(kid.shape)
    cyst = sitk.GetArrayFromImage(sitk.ReadImage(str(cyst_path))) if cyst_path.is_file() else np.zeros(kid.shape)
    label_array = np.zeros(kid.shape)

    # rare label overlap non rare labels
    label_array[kid == 1] = 1
    label_array[ccrcc == 1] = 2
    label_array[cyst == 1] = 3

    label = sitk.GetImageFromArray(label_array)
    return(label)


def main(args, exp_yml, dir_yml):
    ROOT_DIR = Path(exp_yml['DIR']['ROOT'])
    DATA_DIR = Path(exp_yml['DIR']['DATA'])
    OWN_DIR = Path(exp_yml['DIR']['OWN'])
    IMAGE_NAME = dir_yml['image_name']
    LABEL_NAME = dir_yml['label_name']

    resorce_file_list = sorted((OWN_DIR / 'res').glob('*.nii.gz'))
    if len(resorce_file_list) == 0:
        assert ValueError('resorce_file_list dosen`t find.')
    os.makedirs(OWN_DIR / 'ref', exist_ok=True)
    for res in resorce_file_list:
        if len(LABEL_NAME) != 1:
            LABEL_NAME = [DATA_DIR / res.name.split('.')[0] / label for label in LABEL_NAME]
            label = make_concat_label(LABEL_NAME)

            sitk.WriteImage(label, str(OWN_DIR / 'ref' / res.name))
        else:
            # labelが一つしかないのであれば、ただのコピーで良い
            label = (DATA_DIR / f"case_{res.name.split('.')[0]}" / LABEL_NAME[0])
            shutil.copy(label, str(OWN_DIR / 'ref' / res.name))
        # print(label)
        # label = sitk.GetArrayFromImage(sitk.ReadImage(str(label)))
        # print(type(label), str(OWN_DIR / 'ref' / res.name))
        # sitk.WriteImage(label, str(OWN_DIR / 'ref' / res.name))


if __name__ == "__main__":
    args = ParseArgs()
    exp_yml, dir_yml = get_exp_yml(args)
    if ValidateArgs(args, exp_yml):
        main(args, exp_yml, dir_yml)
