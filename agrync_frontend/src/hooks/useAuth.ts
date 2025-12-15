import {useQuery} from "@tanstack/react-query"
import { getUserInfo } from "../api/AuthAPI"


export const useAuth = () => {


    const { data, isError, isLoading } = useQuery({
        queryKey: ['userInfo'],
        queryFn: getUserInfo,
        retry: false,
        refetchOnWindowFocus: false
    })

    return {data, isError, isLoading}
}