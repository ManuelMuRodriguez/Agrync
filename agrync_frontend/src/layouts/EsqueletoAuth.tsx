import { Outlet } from 'react-router'

export default function EsqueletoAuth() {

    return (
        <>
        <div className="min-h-dvh mx-auto w-full bg-radial-[at_50%_100%] from-white from-50% to-bg-green flex items-center justify-center">  

            <div className='mx-auto -mt-10 mb-12 w-2/5 flex flex-col min-w-sm'>

                <img src="agrync.png" alt="Logo del proyecto" className='scale-60 -mb-8'/>

                <main className=''>
                    <Outlet />
                </main>

            </div>
            
        </div>

        </>
    )
}