import { toast } from "react-toastify";
import { getTemplate, uploadFileModbus } from "../api/filesAPI";
import TablaDispositivosModbus from "../components/ModbusDevicesTable";
import TablaEsclavosModbus from "../components/ModbusSlavesTable";
import TablaVariablesModbus from "../components/ModbusVariablesTable";
import React, { useRef } from "react";
import { useTranslation } from "react-i18next";

export default function ModbusDispositivos() {

  const { t } = useTranslation();
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
        toast.error(t('modbus.unknownError'), {
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
    toast.error(t('modbus.fileTooLarge'));
    return;
  }

    try {
      await uploadFileModbus(file);
      toast.success(t('modbus.uploadSuccess'), {
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
        toast.error(t('modbus.unknownError'), {
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
          {t('modbus.downloadTemplate')}
        </button>
        <button
          onClick={handleUploadClick}
          className="bg-button hover:bg-button-hover text-xl text-white px-4 py-2 rounded"
        >
          {t('modbus.uploadFile')}
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