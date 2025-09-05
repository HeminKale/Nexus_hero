import React from 'react';

interface UniversalFieldDisplayProps {
  record: any;
  fieldName: string;
  fieldValue: any;
  fieldType?: string;
  referenceTable?: string;
  referenceDisplayField?: string;
  tenantId: string;
  recordId?: string;
  className?: string;
  isClickable?: boolean;
  onClick?: () => void;
}

export const UniversalFieldDisplay: React.FC<UniversalFieldDisplayProps> = ({
  record,
  fieldName,
  fieldValue,
  fieldType,
  referenceTable,
  referenceDisplayField,
  tenantId,
  recordId,
  className = '',
  isClickable = false,
  onClick
}) => {
  // Get the smart field value (handles __a suffixes, etc.)
  const getSmartFieldValue = (record: any, fieldName: string): any => {
    let fieldValue = record[fieldName];
    
    // If not found, try with __a suffix
    if (fieldValue === undefined && !fieldName.endsWith('__a')) {
      fieldValue = record[`${fieldName}__a`];
    }
    
    // If still not found, try with _a suffix
    if (fieldValue === undefined && !fieldName.endsWith('_a')) {
      fieldValue = record[`${fieldName}_a`];
    }
    
    // If still not found, try snake_case version
    if (fieldValue === undefined) {
      const snakeCase = fieldName.replace(/([A-Z])/g, '_$1').toLowerCase();
      fieldValue = record[snakeCase];
    }
    
    // If still not found, try snake_case with __a suffix
    if (fieldValue === undefined) {
      const snakeCase = fieldName.replace(/([A-Z])/g, '_$1').toLowerCase();
      fieldValue = record[`${snakeCase}__a`];
    }
    
    return fieldValue;
  };

  const smartValue = getSmartFieldValue(record, fieldName);
  
  // For reference fields, the value should already be resolved to a name
  // For non-reference fields, return the smart value or original value
  const displayValue = smartValue || fieldValue || '-';
  
  // Enhanced logging for reference fields
  if (fieldType === 'reference') {
    console.log(`🔍 [UniversalFieldDisplay] === REFERENCE FIELD DISPLAY ===`);
    console.log(`🔍 Field: ${fieldName}`);
    console.log(`🔍 Props:`, {
      fieldName,
      fieldValue,
      fieldType,
      referenceTable,
      referenceDisplayField,
      tenantId,
      recordId
    });
    console.log(`🔍 Record object:`, record);
    console.log(`🔍 Smart value:`, smartValue);
    console.log(`🔍 Final display value:`, displayValue);
    console.log(`🔍 Is this a UUID?`, typeof displayValue === 'string' && displayValue.length === 36);
    console.log(`🔍 Is this a valid reference?`, referenceTable && (referenceDisplayField || 'Using fallback'));
    
    // Check if this looks like an unresolved reference field
    if (typeof displayValue === 'string' && displayValue.length === 36 && referenceTable) {
      if (!referenceDisplayField) {
        console.warn(`⚠️ [UniversalFieldDisplay] Reference field ${fieldName} has no reference_display_field!`);
        console.warn(`⚠️ This field will use fallback display logic (defaulting to 'name' field).`);
        console.warn(`⚠️ Reference table: ${referenceTable}, Display field: null (using fallback)`);
        console.warn(`⚠️ Current value: ${displayValue}`);
      } else {
        console.warn(`⚠️ [UniversalFieldDisplay] Reference field ${fieldName} is showing UUID instead of name!`);
        console.warn(`⚠️ This suggests the reference field resolution didn't work properly.`);
        console.warn(`⚠️ Reference table: ${referenceTable}, Display field: ${referenceDisplayField}`);
        console.warn(`⚠️ Current value: ${displayValue}`);
      }
    }
    
    console.log(`🔍 === END REFERENCE FIELD DISPLAY ===`);
  }

  const handleClick = () => {
    if (isClickable && onClick) {
      onClick();
    }
  };

  const baseClasses = 'px-3 py-2 text-sm';
  const clickableClasses = isClickable ? 'cursor-pointer hover:bg-gray-100 text-blue-600 hover:text-blue-800 underline font-medium hover:underline-offset-2' : '';
  const finalClasses = `${baseClasses} ${clickableClasses} ${className}`.trim();

  return (
    <div 
      className={finalClasses}
      onClick={handleClick}
    >
      {displayValue}
    </div>
  );
};

// Helper function to format column labels
export const formatColumnLabel = (fieldName: string): string => {
  // Handle special cases first
  if (fieldName === 'name') return 'Name';
  if (fieldName === 'id') return 'ID';
  if (fieldName === 'created_by') return 'Created By';
  if (fieldName === 'updated_by') return 'Updated By';
  if (fieldName === 'created_at') return 'Created At';
  if (fieldName === 'updated_at') return 'Updated At';
  
  // Convert camelCase to Title Case with spaces
  let label = fieldName
    .replace(/([A-Z])/g, ' $1') // Add space before capital letters
    .replace(/^./, str => str.toUpperCase()) // Capitalize first letter
    .trim(); // Remove leading space
  
  // Handle special field names
  if (fieldName === 'certificateNumber') return 'Certificate Number';
  if (fieldName === 'recertificationDate') return 'Recertification Date';
  if (fieldName === 'originalIssueDate') return 'Original Issue Date';
  if (fieldName === 'surveillanceDate') return 'Surveillance Date';
  if (fieldName === 'issueDate') return 'Issue Date';
  if (fieldName === 'channelPartner') return 'Channel Partner';
  if (fieldName === 'ISO standard') return 'ISO Standard';
  if (fieldName === 'billing_date') return 'Billing Date';
  
  return label;
};
