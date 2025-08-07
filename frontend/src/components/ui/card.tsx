import React, { ReactNode } from 'react';

export const Card = ({ children }: { children: ReactNode }) => (
    <div className="p-4 bg-white shadow rounded">{children}</div>
);

export const CardContent = ({ children }: { children: ReactNode }) => (
    <div className="py-2">{children}</div>
);

export const CardHeader = ({ title }: { title: ReactNode }) => (
    <h3 className="text-lg font-bold">{title}</h3>
);

export const CardTitle = ({ children }: { children: ReactNode }) => (
    <div className="text-xl font-semibold">{children}</div>
);