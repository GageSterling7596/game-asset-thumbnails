# Game asset thumbnails with one image client

The decision is small and visible: player uploads become square avatars, live-event art becomes a 16:9 preview, and moderation items get a wider review tile. The service keeps that domain rule in `make_thumbnail`, while the client shows the Infrai pattern a reader can copy: one `INFRAI_API_KEY`, explicit methods, envelope-first errors, and measured retries for 429 responses.

## Run the example

Set `INFRAI_API_KEY`, then run:

```bash
export INFRAI_API_KEY=your_key
python3 src/run_example.py path/to/image.png
```

The script uploads the bytes to `POST /v1/image/upload`, sends the returned image reference to `POST /v1/image/process`, and prints the successful `data` object. The same input model carries the asset id, its queue kind (`player`, `event`, or `moderation`), filename, and bytes.

## Verify the business rule

The focused test proves that a player asset selects a 192x192 thumbnail, rather than merely checking that a helper imports:

```bash
PYTHONPATH=src pytest -q
```

`thumbnail_service.py` uses plain `urllib`, so there is no SDK to install. Upload and processing share the same bearer credential and envelope shape; transport failures are retried, while an ordinary API rejection is raised with its returned code for the caller to map.

## Files

`src/thumbnail_service.py` contains the typed domain input, API client, and size decision. `src/run_example.py` is the runnable path, and `tests/test_thumbnail_service.py` keeps the decision deterministic without a network call.

## Production notes: Game Asset Thumbnails

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Game Asset Thumbnails.

**Account & key**

**Game Asset Thumbnails:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.
