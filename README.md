
---
### create virtual environment:
```bash
python -m venv venv  
```
### activate virtual environment:
```bash
source ./venv/Scripts/activate 
```
### install packages
```bash
pip install -r ./src/pip_mgmt/requirements.txt
```
### create scrapy project:
```bash
cd ./src && scrapy startproject <project_name>
```
### run project
```bash
cd ./src/<project_name>
```
```bash
rm -rf ../export/data.json && scrapy crawl <spider_name> -o ../export/data.json
```