# OpenCV color ball transporter

## Usage
`$ python3 ./transporter.py --help`

![python3 ./transporter.py --help](https://user-images.githubusercontent.com/12410942/41600042-6649142c-7407-11e8-85b8-12be211afbe2.png)

## 驗算法
(TODO)

## Demo
追蹤球：在畫面偏左時送出「右」的指令、偏右時送出「左」的指令、在畫面水平中間 40~60% 送出「前」的指令
> ![Demo catching ball](https://media.giphy.com/media/MmOzxs42qrkMDxxGW9/giphy.gif)

夾球：球心進入綠色目標區塊後，開始嘗試夾球，若連續 N（預設10）個 frame 發現球都維持在綠色區塊內，就視為已抓到，否則視為失敗、重新嘗試
> ![Demo tracking feature](https://media.giphy.com/media/EfpghscqBeCgjekhec/giphy.gif)
