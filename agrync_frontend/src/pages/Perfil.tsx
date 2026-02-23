import { useForm } from "react-hook-form";
import { UserNameForm } from "../types";
import ErrorMessage from "../components/ErrorMessage";
import { useAuth } from '../hooks/useAuth';
import { changeFullName } from "../api/UserAPI";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-toastify";
import { useTranslation } from "react-i18next";

export default function Perfil() {

  const { t } = useTranslation();
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
    toast.error(t('profile.sameName'), {
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
            {t('profile.title')}
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
                        placeholder={t('profile.placeholder')}
                        className={`w-full p-3 outline-0 focus:ring-0 border-2 placeholder:text-gap font-medium text-2xl rounded-lg ${errors.full_name ? 'text-error border-error focus:border-error' : 'border-gap focus:border-button'}`}
                        {...register("full_name", {
                          required: t('profile.nameRequired')
                        })}
                      />
                      {errors.full_name && (
                        <ErrorMessage>{errors.full_name.message}</ErrorMessage>
                      )}
                    </div>
          
          
                  <div>
                    <input
                      type="submit"
                      value={t('profile.saveChanges')}
                      className="bg-button hover:bg-button-hover w-full p-3 rounded-lg text-white font-medium text-2xl cursor-pointer"
                    />
                  </div>
                </form>
      </div>
      </div>
    )
  }