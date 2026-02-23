import { useForm } from "react-hook-form";
import { useMutation } from "@tanstack/react-query";
import { useEffect } from 'react';
import { toast } from "react-toastify"
import { CreatePasswordForm } from "../types";
import ErrorMessage from "../components/ErrorMessage";
import { Link, useNavigate } from "react-router-dom";
import { validateUser } from "../api/AuthAPI";
import { useTranslation } from "react-i18next";

export default function CrearPassword() {

  const { t } = useTranslation();
  const navigate = useNavigate()
  const initialValues: CreatePasswordForm = {
    email: '',
    password: '',
    password_confirmation: ''
  }
  const { register, handleSubmit, watch, formState: { errors, dirtyFields  }, trigger } = useForm({ defaultValues: initialValues, mode: "all", reValidateMode: "onChange", shouldFocusError: true })

  const password = watch('password')

  const {mutate} = useMutation({
    mutationFn: validateUser,
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
      navigate("/login")
    }
  })

  const handleCrearPassword = (formData: CreatePasswordForm) => mutate(formData)
  

  useEffect(() => {
    if (dirtyFields.password) {
      trigger("password_confirmation");
    }
  }, [password, dirtyFields.password]);

  return (
    <div className="mx-auto w-4/6 flex flex-col space-y-12">
      <form
        onSubmit={handleSubmit(handleCrearPassword)}
        className=" flex flex-col space-y-12"
        noValidate
      >

        <div className="space-y-6">

          <div>
            <input
              id="email"
              type="email"
              placeholder="Email"
              className={`w-full p-3 outline-0 focus:ring-0 border-2 placeholder:text-gap bg-bg-white-almost-solid font-medium text-2xl rounded-lg ${errors.email ? 'text-error border-error focus:border-error' : 'border-gap focus:border-button'}`}
              {...register("email", {
                required: t('createPassword.emailRequired'),
                pattern: {
                  value: /[^@]+@[^@]+\.[a-zA-Z]{2,6}/,
                  message: t('login.invalidEmail'),
                },
              })}
            />
            {errors.email && (
              <ErrorMessage>{errors.email.message}</ErrorMessage>
            )}
          </div>

          <div>
            <input
              id="password"
              type="password"
              placeholder="Password"
              className={`w-full p-3 outline-0 focus:ring-0 border-2 placeholder:text-gap bg-bg-white-almost-solid font-medium text-2xl rounded-lg  ${errors.password ? 'text-error border-error focus:border-error' : 'border-gap focus:border-button'}`}
              {...register("password", {
                required: t('createPassword.passwordRequired'),
                minLength: {
                  value: 8,
                  message: t('createPassword.passwordMinLength')
                }
              })}
            />
            {errors.password && (
              <ErrorMessage>{errors.password.message}</ErrorMessage>
            )}
          </div>

          <div>
            <input
              id="password_confirmation"
              type="password"
              placeholder={t('createPassword.repeatPassword')}
              className={`w-full p-3 outline-0 focus:ring-0 border-2 placeholder:text-gap bg-bg-white-almost-solid font-medium text-2xl rounded-lg  ${errors.password_confirmation ? 'text-error border-error focus:border-error' : 'border-gap focus:border-button'}`}
              {...register("password_confirmation", {
                required: t('createPassword.confirmRequired'),
                validate: value => value === password || t('createPassword.passwordMismatch')
              })}
            />
            {errors.password_confirmation && (
              <ErrorMessage>{errors.password_confirmation.message}</ErrorMessage>
            )}
          </div>

        </div>


        <div>
          <input
            type="submit"
            value={t('createPassword.activate')}
            className="bg-button hover:bg-button-hover w-full p-3 rounded-lg  text-white font-medium text-2xl cursor-pointer"
          />
        </div>
      </form>

      <nav className="text-center">
            <Link
              to={'/login'}
              className="text-text-green hover:underline font-bold text-lg"
            
            >Have you already activated your password? Log in here.</Link>
      </nav>
    </div>
  )
}