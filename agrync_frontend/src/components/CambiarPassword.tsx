import { useForm } from "react-hook-form";
import { useEffect } from 'react';
import ErrorMessage from "../components/ErrorMessage";
import { ChangePasswordForm } from "../types";
import { changePassword } from "../api/UserAPI";
import { useAuth } from "../hooks/useAuth";
import { useMutation } from "@tanstack/react-query";
import { toast } from "react-toastify";

export default function CambiarPassword() {

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
            Change password
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
                  placeholder="Current password"
                  className={`w-full p-3 outline-0 focus:ring-0 border-2 placeholder:text-gap font-medium text-2xl rounded-lg ${errors.password ? 'text-error border-error focus:border-error' : 'border-gap focus:border-button'}`}
                  {...register("password", {
                    required: "You must enter your current password"
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
                  placeholder="New password"
                  className={`w-full p-3 outline-0 focus:ring-0 border-2 placeholder:text-gap font-medium text-2xl rounded-lg  ${errors.new_password ? 'text-error border-error focus:border-error' : 'border-gap focus:border-button'}`}
                  {...register("new_password", {
                    required: "The new password cannot be empty",
                    minLength: {
                      value: 8,
                      message: 'The password must be at least 8 characters long'
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
                  placeholder="Repeat new password"
                  className={`w-full p-3 outline-0 focus:ring-0 border-2 placeholder:text-gap font-medium text-2xl rounded-lg  ${errors.new_password_confirmation ? 'text-error border-error focus:border-error' : 'border-gap focus:border-button'}`}
                  {...register("new_password_confirmation", {
                    required: "Repeating the new password is mandatory",
                    validate: value => value === new_password || "The new passwords do not match"
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
                value='Save New Password'
                className="bg-button hover:bg-button-hover w-full p-3 rounded-lg  text-white font-medium text-2xl cursor-pointer"
              />
            </div>
          </form>
    

        </div>
       
      )


}