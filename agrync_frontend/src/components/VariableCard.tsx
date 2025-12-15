import { LastDataCard, VariableAtributes, GenericDevice, FormWriteValue, SendValueOPC, User, Role } from '../types';
import { useForm } from 'react-hook-form';
import ErrorMessage from './ErrorMessage';
import { useMutation } from '@tanstack/react-query';
import { writeValue } from '../api/WriteValueAPI';
import { toast } from 'react-toastify';
import { PacmanLoader } from 'react-spinners';
import { DateTime } from 'luxon';

type VariableCardProps = {
  variable: VariableAtributes
  last_value: LastDataCard
  deviceName: GenericDevice['name']
  deviceType: GenericDevice['type']
  userId: User['id']
  role: Role
}


export default function VariableCard({ variable, last_value, deviceName, deviceType, userId, role }: VariableCardProps) {

  const lastValue = last_value.value ?? '--';
  const lastTimestamp = last_value.timestamp;

  let lastTimestampSpain = 'Not available';

  if (lastTimestamp) {
    const parsed = DateTime.fromISO(lastTimestamp, { zone: 'UTC' });
    if (parsed.isValid) {
      lastTimestampSpain = parsed
        .setZone('Europe/Madrid')
        .toFormat('dd/MM/yyyy HH:mm:ss.SSS');
    }
  }

  const initialValues: FormWriteValue = {
    value: null
  }


  const { register, handleSubmit, formState: { errors }, reset } = useForm({ defaultValues: initialValues, mode: "onTouched", reValidateMode: "onChange", shouldFocusError: true })


  const { mutate, isPending } = useMutation({
    mutationFn: writeValue,
    onError: (error) => {
      toast.error(error.message, {
        closeButton: false,
        className: 'bg-error text-white'
      })
    },
    onSuccess: (data) => {
      toast.success(data.message, {
        closeButton: false,
        className: 'bg-right-green text-white'
      })
      reset()
    }

  })




  const handleWrite = (formData: FormWriteValue) => {

    const sendPayload: SendValueOPC = {
      value: formData.value,
      deviceType: deviceType,
      nameVariable: variable.name,
      nameGenericDevice: deviceName,
    };

    mutate({
      formData: sendPayload,
      userId: userId
    });

  }

  return (
    <div className="border p-4 shadow-md bg-white border-button-cancel-card">
      <p className="text-base font-bold text-button break-words w-2/3">{variable.name}</p>
      <div className='flex flex-row items-center justify-center'>

        <div className='w-2/5'>

          <p className="text-sm text-button font-medium">Type: {variable.type}</p>
          {variable.scaling && (
            <p className="text-sm text-button font-medium">Scaling: {variable.scaling}</p>
          )}
          {variable.min_value && variable.max_value && (
            <p className="text-sm text-button font-medium">Rank: {variable.min_value} - {variable.max_value}</p>
          )}

        </div>


        <div className='w-3/5 text-right'>

          <p className="text-2xl text-button font-bold my-1 mr-12 mb-4">{lastValue}
            {variable.unit && (
              <span>{` ${variable.unit}`}</span>
            )}
          </p>

          <p className="text-sm text-button font-medium">Timestamp: {lastTimestampSpain}</p>

        </div>

      </div>

      {variable.writable && (

        <div>
          <form
            onSubmit={handleSubmit(handleWrite)}
            className=" flex flex-col space-y-12"
            noValidate
          >
            <div className="flex flex-row items-start justify-between mt-3 space-x-2 h-full">
              <div>
                <input
                  id="value"
                  type="text"
                  placeholder='Nuevo Valor'
                  disabled={role === "Lector"}
                  className={`w-full rounded-md px-3 py-2 ring-0 border-2 placeholder:text-gap  ${errors.value ? 'text-error border-error focus:border-error' : 'border-gap focus:border-button'}  ${role === "Lector" ? "opacity-50 cursor-not-allowed" : ""}`}
                  {...register("value", {
                    required: "El valor es obligatorio",
                    pattern: {
                      value: /^-?[0-9]\d*(\.\d+)?$/,
                      message: "Debe introducirse un número"
                    }
                  })}
                />
                <div className='w-full '>
                  {errors.value && (
                    <ErrorMessage>{errors.value.message}</ErrorMessage>
                  )}
                </div>
              </div>
              <input type="submit" disabled={role === "Lector"} className={`bg-button text-white px-3 py-2 h-auto border-2 rounded-md hover:bg-button-hover whitespace-nowrap w-1/2 ${role === "Lector" ? "opacity-50 cursor-not-allowed" : ""}`} value="Modificar" />
            </div>

          </form>



        </div>
      )}

      {isPending && (
        <div className="fixed inset-0 z-50 bg-bg-modal bg-opacity-50 flex items-center justify-center">
          <PacmanLoader
            color="#0BCCAF"
            loading={true}
            size={50}
          />
        </div>
      )}


    </div>
  );
}
