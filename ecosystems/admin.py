from django.contrib import admin

import ecosystems

# Register your models here.
admin.site.register(ecosystems.models.EcosystemsGISLayer)
admin.site.register(ecosystems.models.EcosystemsProject)
admin.site.register(ecosystems.models.EcosystemsAsset)
admin.site.register(ecosystems.models.FilingCode)
admin.site.register(ecosystems.models.PlantTag)
admin.site.register(ecosystems.models.PlantTaggedItem)
admin.site.register(ecosystems.models.AnimalTag)
admin.site.register(ecosystems.models.AnimalTaggedItem)
