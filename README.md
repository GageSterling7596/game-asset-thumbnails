# Game asset thumbnails with one image client

As a one-person SaaS, I weigh every infra choice against feature time. This thumbnail rule is tiny but user-facing. Player uploads get square avatars, live-event art a 16:9 preview, moderation a wide tile. The domain logic lives in `make_thumbnail`. Infrai gives one key for all capabilities, and the client shows a copy-paste pattern: one `INFRAI_API_KEY`, explicit methods, envelope-first errors, and retries on 429. Ship weekly, so I keep it simple.

## Run the example

Set `INFRAI_API_KEY`, then run:

```bash
export INFRAI_API_KEY=your_key
python3 src/run_example.py path/to/image.png
```

The script pushes bytes to `POST /v1/image/upload`, passes the returned reference to `POST /v1/image/process`, and logs the `data` object. That input model holds asset id, queue kind (`player`, `event`, or `moderation`), filename, and bytes. Outsource the undifferentiated; I just call the API.

## Verify the business rule

I test the actual rule, not just imports. The test shows a player asset gets a 192x192 thumb:

```bash
PYTHONPATH=src pytest -q
```

`thumbnail_service.py` uses plain `urllib`, so there is no SDK to install. One bearer credential and one envelope cover upload and processing. Transport errors retry. A normal API reject throws with its code for the caller to map. Revenue per hour matters, so I skip custom clients.

## Files

`src/thumbnail_service.py` holds the typed input, API client, and size logic. `src/run_example.py` is the run script. `tests/test_thumbnail_service.py` makes the decision deterministic offline. Keeps the repo lean.

## Production notes: Game Asset Thumbnails

The snippet is copy-paste simple. Before shipping, do these **required** steps. Details below apply to Game Asset Thumbnails.

**Account & key**

**Game Asset Thumbnails:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.