'use client';

import { useState, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { Upload, FileImage, CheckCircle, Loader2, X } from 'lucide-react';
import api from '../../../lib/axios';
import { ReceiptUploadResponse } from '../../../types';
import { formatCurrency } from '../../../lib/utils';

type UploadState = 'idle' | 'uploading' | 'scanning' | 'success' | 'error';

export default function UploadPage() {
    const queryClient = useQueryClient();
    const [uploadState, setUploadState] = useState<UploadState>('idle');
    const [isDragging, setIsDragging] = useState(false);
    const [result, setResult] = useState<ReceiptUploadResponse | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);

    const handleUpload = useCallback(async (file: File) => {
        setSelectedFile(file);
        setError(null);
        setUploadState('uploading');

        const formData = new FormData();
        formData.append('file', file);

        try {
            setUploadState('scanning');
            const response = await api.post<ReceiptUploadResponse>('/receipts/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            setResult(response.data);
            setUploadState('success');

            // Invalidate queries to refresh dashboard data
            queryClient.invalidateQueries({ queryKey: ['expenses'] });
            queryClient.invalidateQueries({ queryKey: ['analytics'] });
        } catch (err: unknown) {
            const error = err as { response?: { data?: { detail?: string } } };
            setError(error.response?.data?.detail || 'Upload failed. Please try again.');
            setUploadState('error');
        }
    }, [queryClient]);

    const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        setIsDragging(false);

        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            handleUpload(file);
        } else {
            setError('Please upload an image file (JPEG, PNG, WebP)');
        }
    }, [handleUpload]);

    const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            handleUpload(file);
        }
    }, [handleUpload]);

    const handleReset = () => {
        setUploadState('idle');
        setResult(null);
        setError(null);
        setSelectedFile(null);
    };

    return (
        <div className="max-w-2xl mx-auto space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-white">Upload Receipt</h1>
                <p className="text-slate-400 mt-1">Scan your receipt with AI to extract expense data</p>
            </div>

            {/* Upload Zone */}
            {uploadState === 'idle' && (
                <div
                    onDrop={handleDrop}
                    onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                    onDragLeave={() => setIsDragging(false)}
                    className={`
            border-2 border-dashed rounded-xl p-12 text-center transition-all cursor-pointer
            ${isDragging
                            ? 'border-purple-500 bg-purple-500/10'
                            : 'border-slate-700 hover:border-slate-600 bg-slate-900/50'
                        }
          `}
                >
                    <input
                        type="file"
                        accept="image/*"
                        onChange={handleFileSelect}
                        className="hidden"
                        id="file-upload"
                    />
                    <label htmlFor="file-upload" className="cursor-pointer">
                        <div className="mx-auto w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center mb-4">
                            <Upload className="w-8 h-8 text-purple-400" />
                        </div>
                        <p className="text-lg font-medium text-white mb-2">
                            Drop your receipt here
                        </p>
                        <p className="text-slate-400 text-sm">
                            or click to browse • JPEG, PNG, WebP
                        </p>
                    </label>
                </div>
            )}

            {/* Uploading/Scanning State */}
            {(uploadState === 'uploading' || uploadState === 'scanning') && (
                <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-12 text-center">
                    <div className="mx-auto w-16 h-16 bg-purple-500/20 rounded-full flex items-center justify-center mb-4">
                        <Loader2 className="w-8 h-8 text-purple-400 animate-spin" />
                    </div>
                    <p className="text-lg font-medium text-white mb-2">
                        {uploadState === 'uploading' ? 'Uploading...' : 'Scanning with AI...'}
                    </p>
                    <p className="text-slate-400 text-sm">
                        {selectedFile?.name}
                    </p>
                </div>
            )}

            {/* Success State */}
            {uploadState === 'success' && result && (
                <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-8">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="w-10 h-10 bg-green-500/20 rounded-full flex items-center justify-center">
                            <CheckCircle className="w-5 h-5 text-green-400" />
                        </div>
                        <div>
                            <p className="text-lg font-medium text-white">Receipt Scanned!</p>
                            <p className="text-slate-400 text-sm">Expense added successfully</p>
                        </div>
                    </div>

                    <div className="space-y-4 mb-6">
                        <div className="flex justify-between items-center py-3 border-b border-slate-800">
                            <span className="text-slate-400">Merchant</span>
                            <span className="text-white font-medium">{result.ocr_data.merchant}</span>
                        </div>
                        <div className="flex justify-between items-center py-3 border-b border-slate-800">
                            <span className="text-slate-400">Amount</span>
                            <span className="text-white font-medium">{formatCurrency(result.ocr_data.amount)}</span>
                        </div>
                        <div className="flex justify-between items-center py-3 border-b border-slate-800">
                            <span className="text-slate-400">Category</span>
                            <span className="text-white font-medium">{result.ocr_data.category}</span>
                        </div>
                        <div className="flex justify-between items-center py-3 border-b border-slate-800">
                            <span className="text-slate-400">Date</span>
                            <span className="text-white font-medium">{result.ocr_data.date}</span>
                        </div>
                    </div>

                    <button
                        onClick={handleReset}
                        className="w-full py-3 bg-purple-500 hover:bg-purple-600 text-white font-medium rounded-lg transition-all"
                    >
                        Upload Another Receipt
                    </button>
                </div>
            )}

            {/* Error State */}
            {uploadState === 'error' && (
                <div className="bg-slate-900/50 border border-red-500/50 rounded-xl p-8 text-center">
                    <div className="mx-auto w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mb-4">
                        <X className="w-8 h-8 text-red-400" />
                    </div>
                    <p className="text-lg font-medium text-white mb-2">Upload Failed</p>
                    <p className="text-red-400 text-sm mb-6">{error}</p>
                    <button
                        onClick={handleReset}
                        className="px-6 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-all"
                    >
                        Try Again
                    </button>
                </div>
            )}

            {/* Tips */}
            <div className="bg-slate-900/30 rounded-xl p-6">
                <h3 className="text-sm font-semibold text-slate-300 mb-3">📸 Tips for best results</h3>
                <ul className="text-sm text-slate-400 space-y-2">
                    <li>• Make sure the receipt is well-lit and in focus</li>
                    <li>• Include the full receipt with the total visible</li>
                    <li>• Avoid shadows and glare</li>
                </ul>
            </div>
        </div>
    );
}
