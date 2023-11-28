# Currency API
Simple API which returns the specified currency value for the specified date.


## Local setup
```bash
python3.11 -m venv venv
```
```bash
pip install -r requirements.txt
```

### Launch the app

```bash
flask --app currency_api.py run --debug
```

### Tests
```bash
pytest -v test_tools.py
```

### Endpoint
We have only one endpoint:
```
/<date>/<currency>
```
For example:
```
http://localhost:5000/2023-11-10/SEK
```
It returns:
```
{
  "currency": "SEK",
  "date": "2023-11-10",
  "value": 11.629
}
```
