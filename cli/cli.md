
---
### create python virtual environment :
```bash
python -m venv venv  
```
---
### activate virtual environment:
```bash
source ./venv/Scripts/activate 
```
---
### install packages:
```bash
pip install -r ./src/pip_mgmt/requirements.txt
```
---
### start crawl data:
general: 
```bash
rm -rf ../export/output.json && scrapy crawl crawl_company -o ../export/output.json
```
crawl company data:
```bash
cd ./src/crawl_company
```
```bash
rm -rf ../export/data_company.json && scrapy crawl crawl_company -o ../export/data_company.json
```
crawl job data:
```bash
cd ./src/crawl_job
```
```bash
rm -rf ../export/data_job.json && scrapy crawl crawl_job -o ../export/data_job.json
```