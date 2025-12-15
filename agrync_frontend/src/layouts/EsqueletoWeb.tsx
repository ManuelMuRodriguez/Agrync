import {  Navigate, Outlet } from 'react-router-dom';
import Menu from '../components/Menu'
import { useAuth } from '../hooks/useAuth'
import { PacmanLoader } from "react-spinners";

export default function EsqueletoWeb() {

    const { data, isError, isLoading } = useAuth()

    if(isError) {
        return <Navigate to='/login' />
    }

    if(data) return (
        <>
        <div className='min-h-dvh mx-8 py-8 flex flex-row'> 
            <div className='sticky top-8 w-82 container flex-shrink-0 bg-bg-section-outline rounded-3xl flex flex-col min-h-[536px] max-h-[calc(100dvh-4rem)] '>

                <img src="/agrync.png" alt="Logo del proyecto" className='mt-7.5 mb-6 scale-85'/>

                <Menu role={data.role} />

            </div> 
            <main className='flex-grow min-w-0'>
                <Outlet />
            </main>
        </div>

        {isLoading && (
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
