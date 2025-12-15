import { useForm } from "react-hook-form";
import { UserNameForm } from "../types";
import ErrorMessage from "../components/ErrorMessage";
import { useAuth } from '../hooks/useAuth';
import { changeFullName } from "../api/UserAPI";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-toastify";

export default function Perfil() {

  const queryClient = useQueryClient();
  const { data } = useAuth();

  const initialValues: UserNameForm = {
      full_name: data?.full_name ?? ''
  }

  const { register, handleSubmit, formState: { errors } } = useForm({ defaultValues: initialValues, mode: "onTouched", reValidateMode: "onChange", shouldFocusError: true })

  
  const {mutate} = useMutation({
      mutationFn: changeFullName,
      onError: (error) => {
        toast.error(error.message, {
        closeButton: false,
        className: 'bg-error text-white'
        })
      },
      onSuccess: (data) => {
        toast.success(data, {
        closeButton: false,
        className: 'bg-right-green text-white'
        })
        queryClient.removeQueries({ queryKey: ['userInfo'] });
      }
      
    })




  const handleName = (formData: UserNameForm) => {
  const userId = data?.id;

  if (formData.full_name === data?.full_name) {
    toast.error("The name you are trying to enter is the same as the current one", {
      closeButton: false,
      className: 'bg-error text-white'
    });
    return;  
  }

    if (userId) {
      mutate({ formData, userId });
    }
  };

    return (
      <div className="mx-auto w-fit">
      <div className="flex flex-col items-start space-y-12">

          <h2 className=" text-4xl text-button text-center font-bold">
            Change username
          </h2>

          <form
                  onSubmit={handleSubmit(handleName)}
                  className=" flex flex-col space-y-10 ml-5"
                  noValidate
                >
          
                    <div>
                      <input
                        id="full_name"
                        type="text"
                        placeholder="User name"
                        className={`w-full p-3 outline-0 focus:ring-0 border-2 placeholder:text-gap font-medium text-2xl rounded-lg ${errors.full_name ? 'text-error border-error focus:border-error' : 'border-gap focus:border-button'}`}
                        {...register("full_name", {
                          required: "The name cannot be left blank."
                        })}
                      />
                      {errors.full_name && (
                        <ErrorMessage>{errors.full_name.message}</ErrorMessage>
                      )}
                    </div>
          
          
                  <div>
                    <input
                      type="submit"
                      value='Guardar Cambios'
                      className="bg-button hover:bg-button-hover w-full p-3 rounded-lg text-white font-medium text-2xl cursor-pointer"
                    />
                  </div>
                </form>
      </div>
      </div>
    )
  }