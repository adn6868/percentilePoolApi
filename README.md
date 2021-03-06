This is a homework submission, feels free to copy and re-distributed

# Install Library
I highly recommend you using [virtualenv](https://pypi.org/project/virtualenv/) for this project.
All dependency library is listed in `requirements.txt`, to install all of them run

`pip install -r requirements.txt`

# Host API on your localhost
You can run `main.py` app with

`python3 main.py`

API should be host on http://127.0.0.1:8000

since fastApi do all the docs, you can try out the API at 

http://127.0.0.1:8000/docs

For development, use `hypercorn` instead as it come with `--reload` option, allow you to live update code:

`hypercorn main:app --reload`

# POST request Schema

ADDPool:

send a post request with query: `http://127.0.0.1:8000/pools/addPool`
Body MUST be included with a json file with the following schema:
```
{
    "poolId" : 0,
    "poolValues" : [
        1, 2, 3
        ]
}
```

responsed for this post should be a json file:
```
{
    'poolId': 0,
    'status': 'inserted'
}
```
or 
```
{
    'poolId': 0,
    'status': 'appended'
}
```

Percentile:

send a post request with query `http://127.0.0.1:8000/pools/getPercentile`
Body MUST be included with a json file with the following schema:

```
{
    "poolId" : 0,
    "percentile" : 11.3
}
```
responsed for this post should be a json file:
```
{
    "poolId": 0,
    "poolLength": 18,
    "percentile": 22.431999999999945
}
```


# My approach to this problem
1. I am choosing python and FastAPI and Python because:
- faster development process :rocket: :full_moon_with_face:
- build-in type check at run time 
- come with `docs` so I don't have to 
- async run in the future if necessary
- Never use FastAPI and I want to learn new thing

2. Since I need to optimized appending to the existing pool instead of inserting a new pool, `db` is set to simply be a dictionary where the key is the `poolId`
. This way I get O(1) when calling append on the existing pool.

3. Since the ratio between read:write is 1:10, I need an efficient way to append to an existing pool. For a simple calculation of percentile of pools less than 100 value, I use List.
Once the number of pools element exceeded 100, I convert it to [TDigest](https://github.com/CamDavidsonPilon/tdigest) for a better appending and build-in calculation.

# Testing:
I'm using build-in fastApi unittest `TestClient`, `TestClient` will act as an instance of API and send `requests` call to it base on my test setup.

You can run unittest for this with

```python test_Api.py```

you can change unittest's "scaling-factor" by editing `self.N` on line `28`

Feels free to add more unittest as I run out of time at the very end searching for edge-case of the API :sweat_smile:
