from PIL import Image
import zipfile
import os
from io import BytesIO

from kakalot_scraper.manager.Manager import *


def generate_file_chapter_name(manga_info: MangaInfo, chapter_num: str) -> str:
    """
    Generates a file name for the manga chapter image.

    Args:
        manga_info (MangaInfo): The information about the manga.
        chapter_num (str): The chapter number.

    Returns:
        str: The generated file name.
    """
    safe_title = manga_info.title.replace(" ", "_").replace("/", "-")
    return f"chapter_{chapter_num}_{safe_title}.cbz"


def decode_file_name(file_name: str) -> tuple[str, str]:
    """
    Decodes the manga title and chapter number from the file name.

    Args:
        file_name (str): The file name to decode.

    Returns:
        tuple[str, str]: A tuple containing the manga title and chapter number.
    """
    # Split the file name to extract the title and chapter number
    base_name = file_name.replace(".cbz", "")
    chapter, title = base_name.split("_", 2)[1:]
    return title.replace("_", " ").replace("-", "/"), chapter


def format_chapter_number(chapter_num: str) -> str:

    chapter = chapter_num.replace("_", ".").lower().strip()
    try:
        formatted = int(float(chapter))
        return f"{formatted}"
    except ValueError:
        pass

    try:
        formatted = f"{float(chapter):.1f}"
        if formatted.endswith(".0"):
            formatted = formatted[:-2]
        return formatted
    except ValueError:
        pass

    return chapter_num


def generate_ComicInfo_xml(manga_info: MangaInfo, chapter_num: str) -> str:
    """
    Generates ComicInfo.xml metadata for the manga chapter.

    Args:
        manga_info (MangaInfo): The information about the manga.
        chapter_num (str): The chapter number.

    Returns:
        str: The generated ComicInfo.xml content.
    """
    xml_template = f"""<?xml version="1.0" encoding="utf-8"?>
<ComicInfo>
    <Title>{manga_info.title}</Title>
    <Series>{manga_info.title}</Series>
    <Number>{format_chapter_number(chapter_num)}</Number>
    <Writer>{manga_info.author}</Writer>
    <Summary>Downloaded from {manga_info.url}</Summary>
    <Web>{manga_info.url}</Web>
    <Genre>{', '.join(manga_info.genres)}</Genre>
</ComicInfo>
"""
    return xml_template


def get_cbz_path(manga_info: MangaInfo, chapter_num: str, save_root: str) -> str:
    manga_file_dir_name = manga_info.title

    cbz_path = os.path.join(
        save_root,
        manga_file_dir_name,
        generate_file_chapter_name(manga_info, chapter_num),
    )
    return cbz_path


def generate_cbz(
    manga_info: MangaInfo, chapter_num: str, images: list[Image.Image], save_root: str
) -> None:

    manga_file_dir_name = manga_info.title

    if not os.path.exists(save_root):
        os.makedirs(save_root)

    if not os.path.exists(os.path.join(save_root, manga_file_dir_name)):
        os.makedirs(os.path.join(save_root, manga_file_dir_name))

    cbz_path = get_cbz_path(manga_info, chapter_num, save_root)

    pre_name = generate_file_chapter_name(manga_info, chapter_num)[:-4]

    if os.path.exists(cbz_path):
        print(f"CBZ already exists at: {cbz_path}, deleting existing file.")
        os.remove(cbz_path)

    with zipfile.ZipFile(cbz_path, "w") as cbz:
        for i, img in enumerate(images):
            img_data = BytesIO()
            img.save(img_data, format="JPEG")
            cbz.writestr(f"{pre_name}_page_{i + 1:04d}.jpg", img_data.getvalue())

        comicinfo_xml = generate_ComicInfo_xml(manga_info, chapter_num)
        cbz.writestr("ComicInfo.xml", comicinfo_xml)

    print(f"CBZ created at: {cbz_path}")
