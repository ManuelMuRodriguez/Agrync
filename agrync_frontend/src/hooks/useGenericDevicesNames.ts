import {useQuery} from "@tanstack/react-query"
import { getUserGenericDevices } from "../api/GenericDevicesApi"
import { useAuth } from "./useAuth";


export const useGenericDevicesNames = () => {

    const { data : authData  } = useAuth();

    const userId = authData?.id

    const { data, isError, isLoading } = useQuery({
        queryKey: ['genericDevicesNames', userId],
        queryFn: () => userId ? getUserGenericDevices(userId) : Promise.resolve([]),
        enabled: !!userId,
        initialData: [],
        retry: false,
        refetchOnWindowFocus: false
    })

    return {data, isError, isLoading}
}