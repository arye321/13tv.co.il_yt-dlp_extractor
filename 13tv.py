from yt_dlp.extractor.common import InfoExtractor
import json


class ThirteenTVIE(InfoExtractor):
    _VALID_URL = (
        r"(?:https?://)?(?:www\.)?13tv\.co\.il/(?P<path>[^/]+/)*(?P<id>[^/?&#]+)"
    )
    _TESTS = [
        {
            # video with vidible ID
            "url": "https://13tv.co.il/item/mood/survivor/season-06/episodes/zxyde-903478422/?pid=903331035&cid=903478422",
            "only_matching": True,
        }
    ]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)
        kaltura_id = self._html_search_regex(
            r'kalturaId":"([^"]+)',
            webpage,
            "kalturaId",
            default=None,
        )
        js = {
            "1": {
                "service": "session",
                "action": "startWidgetSession",
                "widgetId": "_2748741",
            },
            "2": {
                "service": "baseEntry",
                "action": "list",
                "ks": "{1:result:ks}",
                "filter": {"redirectFromEntryId": kaltura_id},
                "responseProfile": {
                    "type": 1,
                    "fields": "id,referenceId,name,description,thumbnailUrl,dataUrl,duration,msDuration,flavorParamsIds,mediaType,type,tags,dvrStatus,externalSourceType,status",
                },
            },
            "3": {
                "service": "baseEntry",
                "action": "getPlaybackContext",
                "entryId": "{2:result:objects:0:id}",
                "ks": "{1:result:ks}",
                "contextDataParams": {
                    "objectType": "KalturaContextDataParams",
                    "flavorTags": "all",
                },
            },
            "4": {
                "service": "metadata_metadata",
                "action": "list",
                "filter": {
                    "objectType": "KalturaMetadataFilter",
                    "objectIdEqual": "{2:result:objects:0:id}",
                    "metadataObjectTypeEqual": "1",
                },
                "ks": "{1:result:ks}",
            },
            "apiVersion": "3.3.0",
            "format": 1,
            "ks": "",
            "clientTag": "html5:v3.13.1",
            "partnerId": "2748741",
        }
        json_data = json.dumps(js).encode("utf-8")
        data = self._download_json(
            "https://cdnapisec.kaltura.com/api_v3/service/multirequest",
            video_id,
            headers={
                "Content-Type": "application/json",
            },
            data=json_data,
        )
        m3u8 = data[2]["sources"][0]["url"]
        formats = self._extract_m3u8_formats(m3u8, video_id, "mp4", fatal=False)
        title = data[1]["objects"][0]["name"]
        return {"id": video_id, "title": title, "formats": formats}
