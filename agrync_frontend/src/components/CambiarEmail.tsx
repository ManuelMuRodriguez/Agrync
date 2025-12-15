import { useForm } from "react-hook-form";
import { useEffect } from 'react';
import ErrorMessage from "../components/ErrorMessage";
import { ChangeEmailForm } from "../types";
import { useMutation } from "@tanstack/react-query";
import { toast } from "react-toastify";
import { changeEmail } from "../api/UserAPI";
import { useAuth } from "../hooks/useAuth";

export default function CambiarEmail() {

    const { data } = useAuth();

    const initialValues: ChangeEmailForm = {
        email: '',
        new_email: '',
        new_email_confirmation: ''
    }

    const { register, handleSubmit, watch, formState: { errors, dirtyFields }, trigger, reset } = useForm({ defaultValues: initialValues, mode: "all", reValidateMode: "onChange", shouldFocusError: true })

    const new_email = watch('new_email')

    const {mutate} = useMutation({
      mutationFn: changeEmail,
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

    const handleChangeEmail = (formData: ChangeEmailForm) => {
      const userId = data?.id;
    
        if (userId) {
          mutate({ formData, userId });
        }
      };



    useEffect(() => {
      if (dirtyFields.new_email) {
        trigger("new_email_confirmation");
      }
    }, [new_email, dirtyFields.new_email]);
    
    return (
      
        <div className="w-1/2 flex flex-col space-y-12 min-w-md">
          
          <h2 className=" text-4xl text-button text-start font-bold">
            Change Email
          </h2>

          <form
            onSubmit={handleSubmit(handleChangeEmail)}
            className=" flex flex-col space-y-12 ml-5 w-2/3"
            noValidate
          >
    
            <div className="space-y-6">
    
              <div>
                <input
                  id="email"
                  type="email"
                  placeholder="Current email"
                  className={`w-full p-3 outline-0 focus:ring-0 border-2 placeholder:text-gap font-medium text-2xl rounded-lg ${errors.email ? 'text-error border-error focus:border-error' : 'border-gap focus:border-button'}`}
                  {...register("email", {
                    required: "You must enter your current email address.",
                    pattern: {
                        value: /[^@]+@[^@]+\.[a-zA-Z]{2,6}/,
                        message: "Email Invalid",
                      }
                  })}
                />
                {errors.email && (
                  <ErrorMessage>{errors.email.message}</ErrorMessage>
                )}
              </div>
    
              <div>
                <input
                  id="new_email"
                  type="email"
                  placeholder="New Email"
                  className={`w-full p-3 outline-0 focus:ring-0 border-2 placeholder:text-gap font-medium text-2xl rounded-lg  ${errors.new_email ? 'text-error border-error focus:border-error' : 'border-gap focus:border-button'}`}
                  {...register("new_email", {
                    required: "The new mailbox cannot be empty",
                    pattern: {
                        value: /[^@]+@[^@]+\.[a-zA-Z]{2,6}/,
                        message: "Email Invalid",
                      },
                  })}
                />
                {errors.new_email && (
                  <ErrorMessage>{errors.new_email.message}</ErrorMessage>
                )}
              </div>
    
              <div>
                <input
                  id="new_email_confirmation"
                  type="email"
                  placeholder="Resend new email"
                  className={`w-full p-3 outline-0 focus:ring-0 border-2 placeholder:text-gap font-medium text-2xl rounded-lg  ${errors.new_email_confirmation ? 'text-error border-error focus:border-error' : 'border-gap focus:border-button'}`}
                  {...register("new_email_confirmation", {
                    required: "Repeat new email",
                    pattern: {
                        value: /[^@]+@[^@]+\.[a-zA-Z]{2,6}/,
                        message: "Invalid email address",
                      },
                    validate: value => value === new_email || "Las nuevas contraseñas no coinciden"

                  })}
                />
                {errors.new_email_confirmation && (
                  <ErrorMessage>{errors.new_email_confirmation.message}</ErrorMessage>
                )}
              </div>
    
            </div>
    
    
            <div>
              <input
                type="submit"
                value='Save new email'
                className="bg-button hover:bg-button-hover w-full p-3 rounded-lg  text-white font-medium text-2xl cursor-pointer"
              />
            </div>
          </form>
    

        </div>
       
      )


}