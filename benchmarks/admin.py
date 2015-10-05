from django.contrib import admin

from .models import (
    Branch,
    Board,
    BoardConfiguration,
    Manifest,
    Result,
    ResultData
)

admin.site.register(Branch)
admin.site.register(Board)
admin.site.register(BoardConfiguration)
admin.site.register(Manifest)
admin.site.register(Result)
admin.site.register(ResultData)
