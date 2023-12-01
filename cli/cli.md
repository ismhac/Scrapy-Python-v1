
```bash
python -m venv venv  
```
```bash
source ./venv/Scripts/activate 
```
```bash
pip install -r ./src/pip_mgmt/requirements.txt
```

```bash
cd ./src/crawl_company
```

```bash
rm -rf ../export/data.json && scrapy crawl crawl_company -o ../export/data.json
```