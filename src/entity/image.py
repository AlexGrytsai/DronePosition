from src.entity import ImagePoint


class Image:
    """
    Клас, що представляє зображення з шириною та висотою.
    """

    def __init__(self, width: int = 640, height: int = 512) -> None:
        self.width = width
        self.height = height

    @property
    def center(self) -> ImagePoint:
        """
        Властивість, що повертає центр зображення.

        Повертає:
            ImagePoint: координати центра зображення
        """
        return ImagePoint(int(self.width / 2), int(self.height / 2))

    def __str__(self) -> str:
        return f"Image({self.width}x{self.height})"
