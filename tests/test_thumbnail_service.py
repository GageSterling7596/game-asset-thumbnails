from thumbnail_service import GameImage, make_thumbnail


class FakeClient:
    def upload(self, image):
        return {"ok": True, "data": {"id": "img_123"}}

    def resize(self, ref, width, height):
        return {"ok": True, "data": {"ref": ref, "width": width, "height": height}}


def test_player_assets_get_square_thumbnails():
    image = GameImage("p1", "player", "avatar.png", b"pixels")
    result = make_thumbnail(FakeClient(), image)
    assert result["data"] == {"ref": "img_123", "width": 192, "height": 192}
