from django.db import models


class MediaCccDeLink(models.Model):
    submission = models.OneToOneField(
        to="submission.Submission",
        on_delete=models.CASCADE,
        related_name="media_ccc_de_link",
    )
    url = models.URLField(max_length=400)
    release_date = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)
    thumbnail_url = models.URLField(null=True, blank=True)

    @property
    def iframe(self):
        return f'<div class="embed-responsive embed-responsive-16by9"><iframe src="{self.url}/oembed" frameborder="0" allowfullscreen></iframe></div>'

    def serialize(self):
        return {
            "submission": self.submission.code,
            "url": self.url,
            "release_date": self.release_date.isoformat()
            if self.release_date
            else None,
            "duration_seconds": self.duration_seconds,
            "thumbnail_url": self.thumbnail_url,
        }
