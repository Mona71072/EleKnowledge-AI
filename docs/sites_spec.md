# sitesテーブル（DynamoDB）の概要
- 現場情報、号機ごとの仕様データを格納する

## プロファイル
- パーテーションキー：sitesNumber (S)
- ソートキー：constructionNumber (S)
- ARN：arn:aws:dynamodb:us-east-1:<LEGACY_US_EAST_1_ACCOUNT_ID>:table/sites

## データ概要
{
  "sitesNumber": {
    "S": "営業番号（現場を区別するため）"
  },
  "constructionNumber": {
    "S": "工事番号（号機を区別するため）"
  },
  "constructionRep": {
    "S": "工事担当者"
  },
  "controlSystem": {
    "S": "制御方式（制御ソフトの種類）"
  },
  "model": {
    "S": "機種"
  },
  "sitesName": {
    "S": "現場名称"
  }
}

## サンプルデータ
{
  "sitesNumber": {
    "S": "UIK5480A"
  },
  "constructionNumber": {
    "S": "EIK54801"
  },
  "constructionRep": {
    "S": "山田一郎"
  },
  "controlSystem": {
    "S": "VFGLF"
  },
  "model": {
    "S": "KE-LG"
  },
  "sitesName": {
    "S": "ベ〇ク川崎"
  }
}
