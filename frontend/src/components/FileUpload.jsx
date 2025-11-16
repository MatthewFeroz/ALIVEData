import React, { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'

export default function FileUpload({ onUpload, disabled = false }) {
  const onDrop = useCallback(
    (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        onUpload(acceptedFiles[0])
      }
    },
    [onUpload]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.bmp'],
    },
    disabled,
    multiple: false,
  })

  return (
    <div
      {...getRootProps()}
      className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
        isDragActive
          ? 'border-alive-active bg-alive-button'
          : 'border-gray-600 hover:border-gray-500'
      } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
    >
      <input {...getInputProps()} />
      {isDragActive ? (
        <p className="text-alive-active">Drop the image here...</p>
      ) : (
        <div>
          <p className="text-gray-400 mb-2">
            Drag & drop an image here, or click to select
          </p>
          <p className="text-sm text-gray-500">
            Supports: PNG, JPG, JPEG, GIF, BMP
          </p>
        </div>
      )}
    </div>
  )
}

