for id in $(cat list.txt); do
  echo "=== $id ==="
  echo "--- tags/$id.en.txt ---"
  cat tags/$id.en.txt
  echo "--- critique/$id.en.txt ---"
  cat critique/$id.en.txt | grep -E "1\. Introduction|2\. Description|3\. Analysis|4\. Interpretation and Evaluation|5\. Conclusion" -A 1
  echo "--- tags/$id.ja.txt ---"
  cat tags/$id.ja.txt
  echo "--- critique/$id.ja.txt ---"
  cat critique/$id.ja.txt | grep -E "1\. 導入|2\. 記述|3\. 分析|4\. 解釈と評価|5\. 結論" -A 1
done
