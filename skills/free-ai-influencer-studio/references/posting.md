# Publishing and analytics

## Tier 0: native scheduling (default, no code)

For each post, build a publish pack in `publish/queue/<date>_<slug>/`: `video.mp4` (passed QC and the license gate), `caption.txt` (with the disclosure line), `cover.jpg` (a clean frame, no fake text), and `meta.json` (scheduled time, platform, series, idea id). The user schedules it in the Instagram app or Meta Business Suite and switches on the platform's AI label when posting. After posting, move the folder to `publish/posted/` and add the post URL to `meta.json`.

## Tier 1: Instagram Graph API from one machine (`scripts/ig_publish.py`)

Requirements (Meta developer documentation, 2026): an Instagram Professional account (Business or Creator) linked to a Facebook Page, a Meta app with the Instagram content publishing permission, and a user access token. For your own account, an app in development mode with your account holding a role on the app is the usual route; serving other people's accounts needs Meta's app review. Long-lived tokens last about 60 days and do not renew themselves, so note the expiry date in `influencer.json` and refresh before it.

Flow the script implements (local file, no public server; available for apps using Facebook Login for Business):

1. `GET /{ig-user-id}/content_publishing_limit?fields=config,quota_usage` to read the live quota. Third-party sources quote 25, 50 or 100 posts per 24 h and even Meta's pages have been inconsistent, so the script trusts the endpoint.
2. `POST https://graph.facebook.com/{version}/{ig-user-id}/media` with `media_type=REELS`, `upload_type=resumable`, `caption`, `share_to_feed=true` (optional `thumb_offset` in ms).
3. `POST https://rupload.facebook.com/ig-api-upload/{version}/{container-id}` with headers `Authorization: OAuth {token}`, `offset: 0`, `file_size: {bytes}` and the file as the body.
4. Poll `GET /{container-id}?fields=status_code` until `FINISHED` (or `ERROR`). On failure, retry once or twice, then create a new container instead of retrying the same one.
5. `POST /{ig-user-id}/media_publish` with `creation_id={container-id}`.

Reels specs to meet before upload: 9:16, H.264 or HEVC in MP4, AAC audio, 1080x1920 recommended; `qc_clip.py` checks these.

Safety defaults in the script: dry run unless `--live`; refuses to run `--live` if the license gate report is missing or failing; never logs the token; reads it from the `IG_ACCESS_TOKEN` environment variable.

AI labelling: if the API offers no label field for your account, add the disclosure line in the caption and keep it in the bio, and apply the in-app label on any post you touch manually. Check Meta's current AI-labelling rules at setup.

## Cadence and timing

Start with 3 to 5 Reels a week. Post times: use the account's own audience-activity data once it exists; before that, pick two slots and alternate them for two weeks, then keep the better one. Series posts go on fixed days so followers learn the rhythm.

## Weekly analytics loop

Pull per-post: reach, plays, average watch time or completion, saves, shares, comments, follows from the post, and product link clicks. Compare each post to the account's own median over the last 4 weeks, not to internet benchmarks. Decide three things: repeat (the format with the best saves plus shares per reach), kill (the bottom performer that was not an experiment), test (one new format or hook). Write them into `influencer.json` under `learnings` with the week number.
