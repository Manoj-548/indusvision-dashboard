from ..models import NexifyProject, NexifyFolder, NexifyImage


def get_or_create_default_folder(project):
    "Get or create default folder for project."
    return NexifyFolder.objects.get_or_create(
        name="default",
        project=project
    )[0]


def upload_single_image(file, project_id):
    "Upload single image to project default folder."
    project = NexifyProject.objects.get(id=project_id)
    folder = get_or_create_default_folder(project)
    image = NexifyImage.objects.create(file=file, folder=folder)
    return image


def upload_bulk_images(files, project_id):
    "Upload multiple images."
    project = NexifyProject.objects.get(id=project_id)
    folder = get_or_create_default_folder(project)
    images = []
    for f in files:
        img = NexifyImage.objects.create(file=f, folder=folder)
        images.append(img)
    return images

