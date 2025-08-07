import React from 'react';
// Button component for the UI
// This component can be customized with additional props as needed
import { ButtonHTMLAttributes } from 'react';

export const Button = ({ children, ...props }: ButtonHTMLAttributes<HTMLButtonElement>) => {
    return (
        <button
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            {...props}
        >
            {children}
        </button>
    );
};
