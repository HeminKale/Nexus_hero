'use client';

import React, { useState, useEffect } from 'react';
import { Upload, FileText, Download, AlertCircle, CheckCircle, Settings, Loader2, Users, Tag } from 'lucide-react';
import FieldEditor from './FieldEditor';
import CertificateGeneratorTabExcel from './CertificateGeneratorTabExcel';
import { createClientSupabaseClient } from '../../lib/supabase';
import { useSupabase } from '../../providers/SupabaseProvider';

interface CertificateGeneratorTabProps {
  tabId: string;
  tabLabel: string;
}

interface ExtractedField {
  name: string;
  value: string;
}

interface ExtractedFields extends Array<ExtractedField> {}

interface ExtractedFieldsObject {
  [key: string]: string;
}

interface Client {
  id: string;
  name: string;
  "ISO standard__a": string | null;
  channelPartner__a: string | null;
  type__a: string | null;
  is_active: boolean;
}

export default function CertificateGeneratorTab({ tabId, tabLabel }: CertificateGeneratorTabProps) {
  const [formDoc, setFormDoc] = useState<File | null>(null);
  const [extractedFields, setExtractedFields] = useState<ExtractedFields>([]);
  const [extractedFieldsObject, setExtractedFieldsObject] = useState<ExtractedFieldsObject>({});
  const [isProcessing, setIsProcessing] = useState(false);
  const [isExtracting, setIsExtracting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isEditingFields, setIsEditingFields] = useState(false);
  
  // New state for client and type selection
  const [clients, setClients] = useState<Client[]>([]);
  const [selectedClient, setSelectedClient] = useState<string>('');
  const [selectedType, setSelectedType] = useState<string>('new');
  const [isLoadingClients, setIsLoadingClients] = useState(false);

  // Get tenant context
  const { userProfile, tenant } = useSupabase();

      // Draft types (hardcoded)
    const certificateTypes = [
    { value: 'new', label: 'New' },
    { value: 'renewal', label: 'Renewal' }
  ];

  // Fetch clients when tenant is available
  useEffect(() => {
    if (tenant?.id) {
      fetchClients();
    }
  }, [tenant]);

  const fetchClients = async () => {
    if (!tenant?.id) {
      setError('No tenant available');
      return;
    }

    setIsLoadingClients(true);
    try {
      const supabase = createClientSupabaseClient();
      
      const { data, error } = await supabase
        .rpc('get_tenant_clients', { p_tenant_id: tenant.id });

      if (error) {
        console.error('Error fetching clients:', error);
        setError('Failed to fetch clients');
        return;
      }

      if (data) {
        setClients(data);
      }
    } catch (err) {
      console.error('Error fetching clients:', err);
      setError('Failed to fetch clients');
    } finally {
      setIsLoadingClients(false);
    }
  };

  const handleFormUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
      setFormDoc(file);
      setError(null);
      setSuccess(null);
      setExtractedFields([]); // Reset extracted fields
    } else {
      setError('Please select a valid Word document (.docx)');
    }
  };

  const extractFields = async () => {
    if (!formDoc) {
      setError('Please select a form file first');
      return;
    }

    if (!selectedClient) {
      setError('Please select a client first');
      return;
    }

    if (!selectedType) {
              setError('Please select a draft type first');
      return;
    }

    setIsExtracting(true);
    setError(null);
    setSuccess(null);

    try {
      const formData = new FormData();
      formData.append('form', formDoc);

      const response = await fetch('/api/pdf/extract-fields', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error("❌ [FRONTEND] API Error:", errorData);
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      setExtractedFields(data.fields || []);
      
      // Transform array to object for FieldEditor
      const fieldsObject: ExtractedFieldsObject = {};
      if (data.fields && Array.isArray(data.fields)) {
        data.fields.forEach((field: ExtractedField) => {
          fieldsObject[field.name] = field.value;
        });
      }
      setExtractedFieldsObject(fieldsObject);
      
      // Debug: Log what fields were extracted
      console.log('🔍 [EXTRACTION] Raw extracted fields:', data.fields);
      console.log('🔍 [EXTRACTION] Transformed fields object:', fieldsObject);
      
      setSuccess('Fields extracted successfully! You can now edit them and generate a draft.');
      
    } catch (err) {
      console.error("❌ [FRONTEND] Field extraction failed:", err);
      setError(err instanceof Error ? err.message : 'Failed to extract fields');
    } finally {
      setIsExtracting(false);
    }
  };

  const handleFieldsChange = (fields: ExtractedFieldsObject) => {
    console.log('🔧 [EDIT] Field changes received:', fields);
    console.log('🔧 [EDIT] Previous extractedFieldsObject:', extractedFieldsObject);
    setExtractedFieldsObject(fields);
    console.log('🔧 [EDIT] Updated extractedFieldsObject:', fields);
  };

  const handleFieldsSave = () => {
    setSuccess('Fields updated successfully!');
    setIsEditingFields(false);
  };

  const handleGenerateCertificate = async () => {
    if (!formDoc || !extractedFieldsObject || Object.keys(extractedFieldsObject).length === 0) {
      setError('Please upload a form and extract fields first');
      return;
    }

    if (!selectedClient || !selectedType) {
              setError('Please select both client and draft type');
      return;
    }

    if (!userProfile?.id) {
      setError('User profile not available');
      return;
    }

    setIsProcessing(true);
    setError(null);
    setSuccess(null);

    try {
      // Step 1: Create draft record BEFORE PDF generation
      const supabase = createClientSupabaseClient();
      
      // Get selected client details for draft creation
      const selectedClientData = clients.find(c => c.id === selectedClient);
      if (!selectedClientData) {
        throw new Error('Selected client not found');
      }

      // Extract company name and address from fields (you may need to adjust these field names)
      // Try multiple possible field names for better extraction
      const companyName = extractedFieldsObject['Company Name'] || 
                         extractedFieldsObject['Company'] || 
                         extractedFieldsObject['Organization'] ||
                         extractedFieldsObject['Client Name'] ||
                         selectedClientData.name;
      
      const address = extractedFieldsObject['Address'] || 
                     extractedFieldsObject['Company Address'] || 
                     extractedFieldsObject['Business Address'] ||
                     extractedFieldsObject['Location'] ||
                     'N/A';
      
      const isoStandard = selectedClientData["ISO standard__a"] || 'N/A';
      
      const scope = extractedFieldsObject['Scope'] || 
                   extractedFieldsObject['Certification Scope'] ||
                   extractedFieldsObject['Audit Scope'] ||
                   extractedFieldsObject['Service Scope'] ||
                   'N/A';

      console.log('🎯 [DRAFT] Creating draft with:', {
        tenant_id: tenant.id,
        client_id: selectedClient,
        type: selectedType,
        company_name: companyName,
        address,
        iso_standard: isoStandard,
        scope,
        created_by: userProfile.id
      });

      // Debug: Log all extracted fields to see what we're working with
      console.log('🔍 [DEBUG] All extracted fields:', extractedFieldsObject);
      console.log('🔍 [DEBUG] Company name sources:', {
        'Company Name': extractedFieldsObject['Company Name'],
        'Company': extractedFieldsObject['Company'],
        'Organization': extractedFieldsObject['Organization'],
        'Client Name': extractedFieldsObject['Client Name'],
        'fallback': selectedClientData.name
      });

      // Create draft record
      const { data: draftResult, error: draftError } = await supabase
        .rpc('create_tenant_draft', {
          p_tenant_id: tenant.id,
          p_client_id: selectedClient,
          p_type: selectedType,
          p_company_name: companyName,
          p_address: address,
          p_iso_standard: isoStandard,
          p_scope: scope,
          p_created_by: userProfile.id
        });

      if (draftError) {
        console.error('❌ [DRAFT] Draft creation failed:', draftError);
        // Continue with PDF generation even if draft fails
        setError('Draft creation failed, but continuing with PDF generation...');
      } else if (draftResult) {
        console.log('✅ [DRAFT] Draft result:', draftResult);
        if (draftResult.success) {
          if (draftResult.is_existing) {
            setSuccess(`Existing draft found: ${draftResult.draft_name}`);
          } else {
            setSuccess(`New draft created: ${draftResult.draft_name}`);
          }
        } else {
          console.warn('⚠️ [DRAFT] Draft creation warning:', draftResult.error);
          // Continue with PDF generation even if draft fails
          setError(`Draft creation warning: ${draftResult.error}, but continuing with PDF generation...`);
        }
      }

      // Step 2: Generate PDF (existing functionality)
      const formData = new FormData();
      formData.append('form', formDoc);
      
      // Create processed fields object with cleaned/extracted values
      const processedFields = {
        ...extractedFieldsObject, // Keep all original extracted fields
        'Address': address,        // Override with cleaned address
        'Company Name': companyName, // Override with cleaned company name
        'Scope': scope,            // Override with cleaned scope
        'ISO Standard': isoStandard // Override with cleaned ISO standard
      };
      
      // Add processed field data as JSON string
      formData.append('fields', JSON.stringify(processedFields));
      
      // Debug: Log what's being sent to PDF generation
      console.log('🔍 [PDF] Sending processed fields to PDF generation:', processedFields);
      console.log('🔍 [PDF] Address field being sent:', processedFields['Address']);

      const response = await fetch('/api/pdf/generate-certificate', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error("❌ [DRAFT] Generation failed:", errorData);
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      
      // Create filename in format: CompanyName_ISOStandard_draft.pdf
      const downloadCompanyName = processedFields['Company Name'] || processedFields['Company'] || 'Unknown';
      const downloadISOStandard = processedFields['ISO Standard'] || 'Unknown';
      
      // Clean company name and ISO standard for filename
      const cleanDownloadCompanyName = downloadCompanyName.replace(/[<>:"/\\|?*]/g, '_').replace(/\s+/g, '_');
      const cleanDownloadISOStandard = downloadISOStandard.replace(/[<>:"/\\|?*]/g, '_').replace(/\s+/g, '_');
      
      a.download = `${cleanDownloadCompanyName}_${cleanDownloadISOStandard}_draft.pdf`;
      
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      setSuccess('Draft generated successfully!');
    } catch (err) {
      console.error("❌ [DRAFT] Generation error:", err);
      setError(err instanceof Error ? err.message : 'Failed to generate draft');
    } finally {
      setIsProcessing(false);
    }
  };

  const resetForm = () => {
    setFormDoc(null);
    setExtractedFields([]);
    setExtractedFieldsObject({});
    setSelectedClient('');
    setSelectedType('new');
    setError(null);
    setSuccess(null);
  };

  // Show loading state if tenant is not yet available
  if (!tenant) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
          <span className="ml-3 text-gray-600">Loading tenant information...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <Settings className="h-6 w-6 text-blue-600" />
          <h2 className="text-2xl font-bold text-gray-900">{tabLabel}</h2>
        </div>
        <div className="mt-2 text-sm text-gray-500">
          <strong>Current Tenant:</strong> {tenant.name}
        </div>
      </div>

      {/* Status Messages */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
          <div className="flex items-center gap-2 text-red-700">
            <AlertCircle className="h-5 w-5" />
            <span>{error}</span>
          </div>
        </div>
      )}

      {success && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-md">
          <div className="flex items-center gap-2 text-green-700">
            <CheckCircle className="h-5 w-5" />
            <span>{success}</span>
          </div>
        </div>
      )}

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Left Column - Existing Content */}
        <div>
          {/* Step 1: Client & Type Selection */}
          <div className="mb-8">
                          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Users className="h-5 w-5 text-blue-600" />
                Step 1: Select Client & Draft Type
              </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Client Dropdown */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Client <span className="text-red-500">*</span>
                </label>
                <select 
                  value={selectedClient}
                  onChange={(e) => setSelectedClient(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                  disabled={isLoadingClients}
                >
                  <option value="">
                    {isLoadingClients ? 'Loading clients...' : 'Select a client...'}
                  </option>
                  {clients.map(client => (
                    <option key={client.id} value={client.id}>
                      {client.name} - {client["ISO standard__a"] || 'No ISO Standard'}
                    </option>
                  ))}
                </select>
                {isLoadingClients && (
                  <div className="mt-2 flex items-center gap-2 text-sm text-gray-500">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Loading clients...
                  </div>
                )}
              </div>
              
              {/* Type Dropdown */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Draft Type <span className="text-red-500">*</span>
                </label>
                <select 
                  value={selectedType}
                  onChange={(e) => setSelectedType(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                >
                  {certificateTypes.map(type => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Selected Client Info */}
            {selectedClient && (
              <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
                <div className="flex items-center gap-2 text-blue-700">
                  <CheckCircle className="h-4 w-4" />
                  <span className="text-sm">
                    Selected: {clients.find(c => c.id === selectedClient)?.name} - {selectedType} draft
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Step 2: Form Upload */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Tag className="h-5 w-5 text-green-600" />
              Step 2: Upload Form Document
            </h3>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors">
              <input
                type="file"
                accept=".docx"
                onChange={handleFormUpload}
                className="hidden"
                id="form-upload"
                disabled={!selectedClient || !selectedType}
              />
              <label htmlFor="form-upload" className={`cursor-pointer ${!selectedClient || !selectedType ? 'opacity-50' : ''}`}>
                {formDoc ? (
                  <div className="flex items-center gap-2 text-blue-600">
                    <FileText className="h-5 w-5" />
                    <span>{formDoc.name}</span>
                  </div>
                ) : (
                  <div className="flex flex-col items-center gap-2 text-gray-500">
                    <Upload className="h-8 w-8" />
                    <span>
                      {!selectedClient || !selectedType 
                        ? 'Please select client and type first' 
                        : 'Click to upload form document'
                      }
                    </span>
                    <span className="text-sm">Supports .docx files</span>
                  </div>
                )}
              </label>
            </div>
            
            {formDoc && (
              <div className="mt-4 flex gap-3">
                <button
                  onClick={extractFields}
                  disabled={isExtracting || !selectedClient || !selectedType}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  {isExtracting ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Extracting Fields...
                    </>
                  ) : (
                    <>
                      <FileText className="h-4 w-4" />
                      Extract Fields
                    </>
                  )}
                </button>
                
                <button
                  onClick={resetForm}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
                >
                  Reset
                </button>
              </div>
            )}
          </div>

          {/* Extracted Fields */}
          {extractedFields.length > 0 && (
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Step 3: Review & Edit Fields
              </h2>
              
              <FieldEditor
                fields={extractedFieldsObject}
                onFieldsChange={handleFieldsChange}
                onSave={handleFieldsSave}
                isEditing={isEditingFields}
                onToggleEdit={() => setIsEditingFields(!isEditingFields)}
              />
            </div>
          )}

          {/* Generate Draft */}
          {Object.keys(extractedFieldsObject).length > 0 && (
            <div className="mb-8">
              <h3 className="text-lg font-semibold mb-4">Step 4: Generate Draft</h3>
              <div className="bg-gray-50 rounded-lg p-6">
                <p className="text-gray-600 mb-4">
                  Ready to generate your draft with the extracted and edited field data.
                </p>
                <button
                  onClick={handleGenerateCertificate}
                  disabled={isProcessing}
                  className="flex items-center gap-2 px-6 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  {isProcessing ? (
                    <>
                      <Loader2 className="h-5 w-5 animate-spin" />
                      Generating Draft...
                    </>
                  ) : (
                    <>
                      <Download className="h-5 w-5" />
                      Generate Draft
                    </>
                  )}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Right Column - Excel Component */}
        <div>
          <CertificateGeneratorTabExcel />
        </div>
      </div>

      {/* Tab Info */}
      <div className="mt-8 p-4 bg-gray-50 rounded-md">
        <h3 className="text-sm font-medium text-gray-700 mb-2">Tab Information</h3>
        <div className="text-xs text-gray-500 space-y-1">
          <p><strong>Tab ID:</strong> {tabId}</p>
          <p><strong>Component Path:</strong> custom/CertificateGeneratorTab</p>
          <p><strong>Type:</strong> Custom Tab</p>
          <p><strong>Features:</strong> Client Selection, Type Selection, Field Extraction, Field Editing, Draft Generation</p>
        </div>
      </div>
    </div>
  );
}
