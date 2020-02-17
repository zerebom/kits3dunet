腎臓がんの自動識別ライブラリ
====


## Description
3DUNetを使って腎臓がんの自動識別を行う。  
限られたメモリの中で精度を出す必要があるため、mhaデータを適切に切り分けて学習する。

以下手順
1. ./src/create_patch.pyを使って、kits2019のデータをミニパッチに分ける
1. experimentの中に実験名を書いたフォルダ(以下A)を作成する
1. Aの中にハイパーパラメータを書いたymlファイルを書く
1. ./src/run_unet_3d_med.pyにymlファイルを渡して学習
1. pred.shを使って推論、プロットを行う

## Requirement
- cuda10.0
- nvidia-driver 430.x.x
- ubuntu 18.04 


## Usage

### create patch
```
# dir内に余計なデータがないように消す
sudo rm -rf ./*/tumor*standard*

for i in `seq -w 000 160`; do
# kits2019が格納されているdir
cd /home/kakeya/ssd/strange/00${i}
pwd
# 使用するnii.gz sizeを選択する
sudo python3 ./src/create_patch2.py SE2.nii.gz SE3.nii.gz kidney.nii.gz CCRCC.nii.gz cyst.nii.gz --size 60 60 20 
sudo python3 ./src/create_patch2.py SE2.nii.gz SE3.nii.gz kidney.nii.gz CCRCC.nii.gz cyst.nii.gz --size 48 48 16
```

## Install
```
pipenv install
pipenv shell
python3 ./src/Keras/run_unet_3d_med.py -yml
```

## Author
[zerebom](https://github.com/zerebom)
## 参考
[pipenvの使い方](https://medium.com/@kjmczk/python-pipenv-2fbcd681f534)