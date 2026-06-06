from pydantic import BaseModel, Field


class PresignRequest(BaseModel):
    filename: str = Field(..., description="Original name of file to upload")
    content_type: str = Field(..., description="MIME content type of target file")
    size: int = Field(..., description="File size in bytes")
    asset_type: str = Field(
        ...,
        description="Type category: product_image, blog_image, certificate_pdf, avatar, packaging_file, video"
    )


class PresignResponse(BaseModel):
    id: str = Field(..., description="Media asset database record identifier")
    upload_url: str = Field(..., description="Presigned PUT URL to upload file directly to storage")
    public_url: str = Field(..., description="Calculated public URL where file will be accessible")
    storage_key: str = Field(..., description="The unique storage path/key allocated for file")


class UploadCompleteRequest(BaseModel):
    id: str = Field(..., description="Media asset database record identifier")
    status: str = Field(..., description="Final status of upload confirmation: completed or failed")


class MediaAssetResponse(BaseModel):
    id: str
    original_filename: str
    content_type: str
    size: int
    storage_key: str
    public_url: str
    uploaded_by: str
    asset_type: str
    status: str
    created_at: str
