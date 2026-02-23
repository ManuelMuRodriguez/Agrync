import { useForm } from "react-hook-form";
import { useEffect } from 'react';
import ErrorMessage from "../components/ErrorMessage";
import { ChangePasswordForm } from "../types";
import { changePassword } from "../api/UserAPI";
import { useAuth } from "../hooks/useAuth";
import { useMutation } from "@tanstack/react-query";
import { toast } from "react-toastify";
import { useTranslation } from "react-i18next";

export default function CambiarPassword() {

    const { t } = useTranslation();
    const { data } = useAuth();
    const initialValues: ChangePasswordForm = {
        password: '',
        new_password: '',
        new_password_confirmation: ''
    }

    const { register, handleSubmit, watch, formState: { errors, dirtyFields }, trigger, reset } = useForm({ defaultValues: initialValues, mode: "all", reValidateMode: "onChange", shouldFocusError: true })

    const new_password = watch('new_password')

    const {mutate} = useMutation({
      mutationFn: changePassword,
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
        reset()
      }
      
    })

    const handleChangePassword = (formData: ChangePasswordForm) => {
      const userId = data?.id;
    
        if (userId) {
          mutate({ formData, userId });
        }
      };


    useEffect(() => {
          if (dirtyFields.new_password) {
            trigger("new_password_confirmation");
          }
        }, [new_password, dirtyFields.new_password]);
    
    return (
      
        <div className="w-1/2 flex flex-col space-y-12 min-w-lg">
          
          <h2 className=" text-4xl text-button text-start font-bold">
            {t('changePassword.title')}
          </h2>

          <form
            onSubmit={handleSubmit(handleChangePassword)}
            className=" flex flex-col space-y-12 ml-5 w-2/3"
            noValidate
          >
    
            <div className="space-y-6">
    
              <div>
                <input
                  id="password"
                  type="password"
                  placeholder={t('changePassword.current')}
                  className={`w-full p-3 outline-0 focus:ring-0 border-2 placeholder:text-gap font-medium text-2xl rounded-lg ${errors.password ? 'text-error border-error focus:border-error' : 'border-gap focus:border-button'}`}
                  {...register("password", {
                    required: t('changePassword.currentRequired')
                  })}
                />
                {errors.password && (
                  <ErrorMessage>{errors.password.message}</ErrorMessage>
                )}
              </div>
    
              <div>
                <input
                  id="new_password"
                  type="password"
                  placeholder={t('changePassword.new')}
                  className={`w-full p-3 outline-0 focus:ring-0 border-2 placeholder:text-gap font-medium text-2xl rounded-lg  ${errors.new_password ? 'text-error border-error focus:border-error' : 'border-gap focus:border-button'}`}
                  {...register("new_password", {
                    required: t('changePassword.newRequired'),
                    minLength: {
                      value: 8,
                      message: t('changePassword.minLength')
                    }
                  })}
                />
                {errors.new_password && (
                  <ErrorMessage>{errors.new_password.message}</ErrorMessage>
                )}
              </div>
    
              <div>
                <input
                  id="new_password_confirmation"
                  type="password"
                  placeholder={t('changePassword.confirm')}
                  className={`w-full p-3 outline-0 focus:ring-0 border-2 placeholder:text-gap font-medium text-2xl rounded-lg  ${errors.new_password_confirmation ? 'text-error border-error focus:border-error' : 'border-gap focus:border-button'}`}
                  {...register("new_password_confirmation", {
                    required: t('changePassword.confirmRequired'),
                    validate: value => value === new_password || t('changePassword.mismatch')
                  })}
                />
                {errors.new_password_confirmation && (
                  <ErrorMessage>{errors.new_password_confirmation.message}</ErrorMessage>
                )}
              </div>
    
            </div>
    
    
            <div>
              <input
                type="submit"
                value={t('changePassword.save')}
                className="bg-button hover:bg-button-hover w-full p-3 rounded-lg  text-white font-medium text-2xl cursor-pointer"
              />
            </div>
          </form>
    

        </div>
       
      )


}