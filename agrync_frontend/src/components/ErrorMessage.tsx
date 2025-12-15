import React from "react";

export default function ErrorMessage({children} : {children: React.ReactNode}) {
    return (
        <p className="text-error font-bold text-sm "> {children} </p>
    )
}