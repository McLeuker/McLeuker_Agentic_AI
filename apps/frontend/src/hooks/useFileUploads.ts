'use client';

import { useState, useCallback, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "@/contexts/AuthContext";

// Types for file uploads
export interface FileUpload {
  id: string;
  user_id: string;
  conversation_id: string | null;
  file_name: string;
  file_type: string;
  file_size: number;
  storage_path: string;
  public_url: string | null;
  mime_type: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface UploadFileInput {
  file: File;
  conversation_id?: string;
  metadata?: Record<string, unknown>;
}

// Allowed file types
const ALLOWED_IMAGE_TYPES = ['image/png', 'image/jpeg', 'image/webp', 'image/gif'];
const ALLOWED_VIDEO_TYPES = ['video/mp4', 'video/mpeg', 'video/quicktime', 'video/x-msvideo'];
const ALLOWED_DOCUMENT_TYPES = ['application/pdf', 'text/plain', 'application/json'];
const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB

export function useFileUploads() {
  const { user } = useAuth();
  const [uploads, setUploads] = useState<FileUpload[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  // Validate file type
  const validateFileType = (file: File): boolean => {
    const allAllowed = [
      ...ALLOWED_IMAGE_TYPES,
      ...ALLOWED_VIDEO_TYPES,
      ...ALLOWED_DOCUMENT_TYPES,
    ];
    return allAllowed.includes(file.type);
  };

  // Validate file size
  const validateFileSize = (file: File): boolean => {
    return file.size <= MAX_FILE_SIZE;
  };

  // Get file type category
  const getFileCategory = (mimeType: string): string => {
    if (ALLOWED_IMAGE_TYPES.includes(mimeType)) return 'image';
    if (ALLOWED_VIDEO_TYPES.includes(mimeType)) return 'video';
    if (ALLOWED_DOCUMENT_TYPES.includes(mimeType)) return 'document';
    return 'other';
  };

  // Load all uploads for the user
  const loadUploads = useCallback(async (conversationId?: string) => {
    if (!user) return;

    setLoading(true);
    setError(null);

    try {
      let query = supabase
        .from("file_uploads")
        .select("*")
        .eq("user_id", user.id)
        .order("created_at", { ascending: false });

      if (conversationId) {
        query = query.eq("conversation_id", conversationId);
      }

      const { data, error: fetchError } = await query;

      if (fetchError) throw fetchError;

      setUploads((data || []) as FileUpload[]);
    } catch (err) {
      console.error("Error loading uploads:", err);
      setError("Failed to load uploads");
    } finally {
      setLoading(false);
    }
  }, [user]);

  // Upload a file to Supabase Storage and track it
  const uploadFile = useCallback(async (input: UploadFileInput): Promise<FileUpload | null> => {
    if (!user) return null;

    const { file, conversation_id, metadata } = input;

    // Validate file
    if (!validateFileType(file)) {
      setError(`File type ${file.type} is not allowed`);
      return null;
    }

    if (!validateFileSize(file)) {
      setError(`File size exceeds maximum limit of ${MAX_FILE_SIZE / 1024 / 1024}MB`);
      return null;
    }

    setUploading(true);
    setUploadProgress(0);
    setError(null);

    try {
      // Generate unique file path
      const fileExt = file.name.split('.').pop();
      const fileName = `${Date.now()}_${Math.random().toString(36).substring(7)}.${fileExt}`;
      const storagePath = `${user.id}/${getFileCategory(file.type)}/${fileName}`;

      // Upload to Supabase Storage
      const { data: storageData, error: storageError } = await supabase.storage
        .from('uploads')
        .upload(storagePath, file, {
          cacheControl: '3600',
          upsert: false,
        });

      if (storageError) throw storageError;

      setUploadProgress(50);

      // Get public URL
      const { data: urlData } = supabase.storage
        .from('uploads')
        .getPublicUrl(storagePath);

      const publicUrl = urlData?.publicUrl || null;

      setUploadProgress(75);

      // Save to database
      const { data, error: dbError } = await supabase
        .from("file_uploads")
        .insert({
          user_id: user.id,
          conversation_id: conversation_id || null,
          file_name: file.name,
          file_type: getFileCategory(file.type),
          file_size: file.size,
          storage_path: storagePath,
          public_url: publicUrl,
          mime_type: file.type,
          metadata: metadata || {},
        })
        .select()
        .single();

      if (dbError) throw dbError;

      setUploadProgress(100);

      const newUpload = data as FileUpload;
      setUploads(prev => [newUpload, ...prev]);

      return newUpload;
    } catch (err) {
      console.error("Error uploading file:", err);
      setError("Failed to upload file");
      return null;
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  }, [user]);

  // Upload multiple files
  const uploadFiles = useCallback(async (files: File[], conversationId?: string): Promise<FileUpload[]> => {
    const results: FileUpload[] = [];

    for (const file of files) {
      const result = await uploadFile({
        file,
        conversation_id: conversationId,
      });
      if (result) {
        results.push(result);
      }
    }

    return results;
  }, [uploadFile]);

  // Delete a file upload
  const deleteUpload = useCallback(async (id: string): Promise<boolean> => {
    if (!user) return false;

    try {
      // Get the upload record first
      const upload = uploads.find(u => u.id === id);
      if (!upload) return false;

      // Delete from storage
      const { error: storageError } = await supabase.storage
        .from('uploads')
        .remove([upload.storage_path]);

      if (storageError) {
        console.warn("Error deleting from storage:", storageError);
        // Continue anyway to delete the database record
      }

      // Delete from database
      const { error: dbError } = await supabase
        .from("file_uploads")
        .delete()
        .eq("id", id)
        .eq("user_id", user.id);

      if (dbError) throw dbError;

      setUploads(prev => prev.filter(u => u.id !== id));
      return true;
    } catch (err) {
      console.error("Error deleting upload:", err);
      setError("Failed to delete upload");
      return false;
    }
  }, [user, uploads]);

  // Get uploads for a conversation
  const getUploadsByConversation = useCallback(async (conversationId: string): Promise<FileUpload[]> => {
    if (!user) return [];

    try {
      const { data, error } = await supabase
        .from("file_uploads")
        .select("*")
        .eq("user_id", user.id)
        .eq("conversation_id", conversationId)
        .order("created_at", { ascending: false });

      if (error) throw error;

      return (data || []) as FileUpload[];
    } catch (err) {
      console.error("Error getting uploads by conversation:", err);
      return [];
    }
  }, [user]);

  // Convert file to base64 for API calls
  const fileToBase64 = useCallback(async (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        const result = reader.result as string;
        // Remove the data URL prefix (e.g., "data:image/png;base64,")
        const base64 = result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = error => reject(error);
    });
  }, []);

  // Load uploads on mount
  useEffect(() => {
    if (user) {
      loadUploads();
    }
  }, [user, loadUploads]);

  return {
    uploads,
    loading,
    uploading,
    uploadProgress,
    error,
    loadUploads,
    uploadFile,
    uploadFiles,
    deleteUpload,
    getUploadsByConversation,
    fileToBase64,
    validateFileType,
    validateFileSize,
    ALLOWED_IMAGE_TYPES,
    ALLOWED_VIDEO_TYPES,
    ALLOWED_DOCUMENT_TYPES,
    MAX_FILE_SIZE,
  };
}
