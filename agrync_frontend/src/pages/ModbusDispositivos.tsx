import { toast } from "react-toastify";
import { getTemplate, uploadFileModbus } from "../api/FilesAPI";
import TablaDispositivosModbus from "../components/TablaDispositivosModbus";
import TablaEsclavosModbus from "../components/TablaEsclavosModbus";
import TablaVariablesModbus from "../components/TablaVariablesModbus";
import React, { useRef } from "react";

export default function ModbusDispositivos() {

  const fileInputRef = useRef<HTMLInputElement>(null);


  const handleDownload = async () => {
    try {
      const blob = await getTemplate();
      const url = window.URL.createObjectURL(new Blob([blob]));
      const a = document.createElement("a");
      a.href = url;
      a.download = "TemplateModbus.json";
      a.click();
      window.URL.revokeObjectURL(url);

    } catch (error: unknown) {
      if (error instanceof Error) {
        toast.error(error.message, {
          closeButton: false,
          className: 'bg-error text-white'
        })
      } else {
        toast.error("Error desconocido", {
          closeButton: false,
          className: 'bg-error text-white'
        })

      }
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const MAX_SIZE_BYTES = 10 * 1024 * 1024;

  const handleFileChange = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (file.size > MAX_SIZE_BYTES) {
    toast.error("The file is too large. The limit is 10 MB.");
    return;
  }

    try {
      await uploadFileModbus(file);
      toast.success("File uploaded successfully", {
        closeButton: false,
        className: 'bg-right-green text-white',
      });
    } catch (error: unknown) {
      if (error instanceof Error) {
        toast.error(error.message, {
          closeButton: false,
          className: "bg-error text-white",
        });
      } else {
        toast.error("Unknown error", {
          closeButton: false,
          className: "bg-error text-white",
        });
      }
    }
  };


  return (
    <div className="space-y-6 mt-6">

      <div className="flex gap-2 mt-4">
        <button
          onClick={handleDownload}
          className="bg-button hover:bg-button-hover text-xl text-white px-4 py-2 rounded"
        >
          Download template
        </button>
        <button
          onClick={handleUploadClick}
          className="bg-button hover:bg-button-hover text-xl text-white px-4 py-2 rounded"
        >
          Upload configuration file
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".json"
          hidden
          onChange={handleFileChange}
        />
      </div>


      <TablaDispositivosModbus />
      <TablaEsclavosModbus />
      <TablaVariablesModbus />
    </div>
  )
}