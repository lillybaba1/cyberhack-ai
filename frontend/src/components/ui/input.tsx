import React from 'react';

export const Input = ({ ...props }) => {
    return (
        <input
            className="border p-2 rounded w-full"
            {...props}
        />
    );
};
