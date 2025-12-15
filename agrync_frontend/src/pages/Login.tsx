import { useForm } from "react-hook-form";
import { UserLoginForm } from "../types";
import ErrorMessage from "../components/ErrorMessage";
import { Link, useNavigate } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { login } from "../api/AuthAPI";
import { toast } from "react-toastify";
import { PacmanLoader } from "react-spinners";

export default function Login() {
  const queryClient = useQueryClient();
  const navigate = useNavigate()
  const initialValues: UserLoginForm = {
    username: '',
    password: '',
  }
  const { register, handleSubmit, formState: { errors } } = useForm({ defaultValues: initialValues, mode: "onTouched", reValidateMode: "onChange", shouldFocusError: true })

  const {mutate, isPending } = useMutation({
    mutationFn: login,
    onError: (error) => {
      toast.error(error.message, {
      closeButton: false,
      className: 'bg-error text-white'
      })
    },
    onSuccess: () => {
      toast.success("Inicio de sesión satisfactorio", {
      closeButton: false,
      className: 'bg-right-green text-white'
      })
      navigate("/dashboard")
      queryClient.removeQueries({ queryKey: ['userInfo'] });
    }
    
  })

  
  

  const handleLogin = (formData: UserLoginForm) => mutate(formData)

  return (
    <>
    <div className="mx-auto w-4/6 flex flex-col space-y-12">
      <form
        onSubmit={handleSubmit(handleLogin)}
        className=" flex flex-col space-y-12"
        noValidate
      >

        <div className="space-y-6">

          <div>
            <input
              id="username"
              type="email"
              placeholder="Email"
              className={`w-full p-3 outline-0 focus:ring-0 border-2 placeholder:text-gap bg-bg-white-almost-solid font-medium text-2xl rounded-lg ${errors.username ? 'text-error border-error focus:border-error' : 'border-gap focus:border-button'}`}
              {...register("username", {
                required: "El email es obligatorio",
                pattern: {
                  value: /[^@]+@[^@]+\.[a-zA-Z]{2,6}/,
                  message: "Invalid email address",
                },
              })}
            />
            {errors.username && (
              <ErrorMessage>{errors.username.message}</ErrorMessage>
            )}
          </div>

          <div>
            <input
              id="password"
              type="password"
              placeholder="Password"
              className={`w-full p-3 outline-0 focus:ring-0 border-2 placeholder:text-gap bg-bg-white-almost-solid font-medium text-2xl rounded-lg  ${errors.password ? 'text-error border-error focus:border-error' : 'border-gap focus:border-button'}`}
              {...register("password", {
                required: "The password is mandatory",

              })}
            />
            {errors.password && (
              <ErrorMessage>{errors.password.message}</ErrorMessage>
            )}
          </div>
        </div>


        <div>
          <input
            type="submit"
            value='Iniciar Sesión'
            disabled={isPending}
            className="bg-button hover:bg-button-hover w-full p-3 rounded-lg text-white font-medium text-2xl cursor-pointer"
          />
        </div>
      </form>

      <nav className="text-center">
            <Link
              to={'/crear-password'}
              className="text-text-green hover:underline font-bold text-lg"
            
            >Haven't activated your account yet? Activate it here.</Link>
      </nav>
    </div>

            {isPending && (
          <div className="fixed inset-0 z-50 bg-bg-modal bg-opacity-50 flex items-center justify-center">
            <PacmanLoader
              color="#0BCCAF"
              loading={true}
              size={50}
            />
          </div>
        )}

    </>
  )
}




