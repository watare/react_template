/**
 * RDF Schema Visualization Page
 *
 * Data flow:
 * - RDF schema data → Fetched from API, stored in component state
 * - Selected class → Local state for UI interaction
 * - Expanded samples → Local state for accordion behavior
 */
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useSCLFiles } from '../hooks/useSCLFiles';

interface RDFClass {
  type: string;
  count: number;
  samples: Array<{
    subject: string;
    predicate: string;
    object: string;
  }>;
}

interface RDFSchema {
  file_id: number;
  filename: string;
  triple_count: number;
  classes: RDFClass[];
  namespaces: string[];
  fuseki_dataset: string;
}

const RDFSchemaPage: React.FC = () => {
  const { fileId } = useParams<{ fileId: string }>();
  const navigate = useNavigate();
  const { getRDFSchema } = useSCLFiles();

  const [schema, setSchema] = useState<RDFSchema | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedClass, setSelectedClass] = useState<string | null>(null);
  const [expandedSamples, setExpandedSamples] = useState<{ [key: string]: boolean }>({});

  useEffect(() => {
    const loadSchema = async () => {
      try {
        setLoading(true);
        const data = await getRDFSchema(Number(fileId));
        setSchema(data);

        // Auto-select first class
        if (data.classes.length > 0) {
          setSelectedClass(data.classes[0].type);
        }
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load RDF schema');
      } finally {
        setLoading(false);
      }
    };

    loadSchema();
  }, [fileId, getRDFSchema]);

  const extractLocalName = (uri: string): string => {
    const parts = uri.split(/[#/]/);
    return parts[parts.length - 1] || uri;
  };

  const toggleSample = (classType: string) => {
    setExpandedSamples(prev => ({
      ...prev,
      [classType]: !prev[classType]
    }));
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-600">Loading RDF schema...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
          <button
            onClick={() => navigate('/scl-files')}
            className="mt-4 text-blue-600 hover:text-blue-800"
          >
            ← Back to files
          </button>
        </div>
      </div>
    );
  }

  if (!schema) {
    return null;
  }

  const selectedClassData = schema.classes.find(c => c.type === selectedClass);

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <button
          onClick={() => navigate('/scl-files')}
          className="text-blue-600 hover:text-blue-800 mb-4"
        >
          ← Back to files
        </button>
        <h1 className="text-3xl font-bold mb-2">RDF Schema Visualization</h1>
        <p className="text-gray-600">
          File: <span className="font-medium">{schema.filename}</span>
        </p>
        <p className="text-sm text-gray-500">
          {schema.triple_count.toLocaleString()} triples in dataset "{schema.fuseki_dataset}"
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sidebar: Classes List */}
        <div className="lg:col-span-1">
          <div className="bg-white border border-gray-200 rounded-lg p-4 sticky top-4">
            <h2 className="text-lg font-semibold mb-4">RDF Classes</h2>
            <div className="space-y-2 max-h-[600px] overflow-y-auto">
              {schema.classes.map((cls) => (
                <button
                  key={cls.type}
                  onClick={() => setSelectedClass(cls.type)}
                  className={`w-full text-left px-3 py-2 rounded transition-colors ${
                    selectedClass === cls.type
                      ? 'bg-blue-100 text-blue-800 border border-blue-300'
                      : 'hover:bg-gray-50 border border-transparent'
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <span className="font-medium text-sm truncate" title={cls.type}>
                      {extractLocalName(cls.type)}
                    </span>
                    <span className="text-xs bg-gray-100 px-2 py-1 rounded-full ml-2">
                      {cls.count}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Main: Class Details */}
        <div className="lg:col-span-2">
          {selectedClassData ? (
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <div className="mb-6">
                <h2 className="text-2xl font-bold mb-2">
                  {extractLocalName(selectedClassData.type)}
                </h2>
                <p className="text-sm text-gray-500 break-all mb-4">
                  {selectedClassData.type}
                </p>
                <div className="inline-block bg-blue-100 text-blue-800 px-4 py-2 rounded-full font-medium">
                  {selectedClassData.count.toLocaleString()} instances
                </div>
              </div>

              {/* Sample Triples */}
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold">Sample Triples</h3>
                  <button
                    onClick={() => toggleSample(selectedClassData.type)}
                    className="text-sm text-blue-600 hover:text-blue-800"
                  >
                    {expandedSamples[selectedClassData.type] ? 'Collapse' : 'Expand'} All
                  </button>
                </div>

                <div className="space-y-4">
                  {selectedClassData.samples.length === 0 ? (
                    <p className="text-gray-500 text-sm">No sample data available</p>
                  ) : (
                    <>
                      {/* Group by subject */}
                      {(() => {
                        const bySubject = selectedClassData.samples.reduce((acc, triple) => {
                          if (!acc[triple.subject]) {
                            acc[triple.subject] = [];
                          }
                          acc[triple.subject].push(triple);
                          return acc;
                        }, {} as Record<string, typeof selectedClassData.samples>);

                        return Object.entries(bySubject).slice(0, 3).map(([subject, triples]) => (
                          <div
                            key={subject}
                            className="border border-gray-200 rounded-lg overflow-hidden"
                          >
                            <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
                              <p className="text-sm font-mono text-gray-700 truncate" title={subject}>
                                {extractLocalName(subject)}
                              </p>
                            </div>
                            <div className="p-4">
                              {expandedSamples[selectedClassData.type] ? (
                                <table className="w-full text-sm">
                                  <thead>
                                    <tr className="border-b border-gray-200">
                                      <th className="text-left py-2 font-medium text-gray-700">Property</th>
                                      <th className="text-left py-2 font-medium text-gray-700">Value</th>
                                    </tr>
                                  </thead>
                                  <tbody>
                                    {triples.map((triple, idx) => (
                                      <tr key={idx} className="border-b border-gray-100">
                                        <td className="py-2 pr-4 font-mono text-xs text-gray-600">
                                          {extractLocalName(triple.predicate)}
                                        </td>
                                        <td className="py-2 font-mono text-xs break-all">
                                          {extractLocalName(triple.object)}
                                        </td>
                                      </tr>
                                    ))}
                                  </tbody>
                                </table>
                              ) : (
                                <div className="text-sm text-gray-600">
                                  {triples.length} properties
                                  <button
                                    onClick={() => toggleSample(selectedClassData.type)}
                                    className="ml-2 text-blue-600 hover:text-blue-800"
                                  >
                                    (show)
                                  </button>
                                </div>
                              )}
                            </div>
                          </div>
                        ));
                      })()}
                    </>
                  )}
                </div>
              </div>

              {/* SPARQL Query Link */}
              <div className="mt-6 pt-6 border-t border-gray-200">
                <h3 className="text-sm font-semibold mb-2 text-gray-700">Query in SPARQL</h3>
                <pre className="bg-gray-50 p-4 rounded text-xs font-mono overflow-x-auto">
                  {`SELECT ?s ?p ?o
WHERE {
  ?s a <${selectedClassData.type}> .
  ?s ?p ?o .
}
LIMIT 100`}
                </pre>
                <a
                  href={`http://localhost:3030/dataset.html?tab=query&dataset=/${schema.fuseki_dataset}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-block mt-4 text-sm text-blue-600 hover:text-blue-800"
                >
                  Open in Fuseki Query Editor →
                </a>
              </div>
            </div>
          ) : (
            <div className="bg-white border border-gray-200 rounded-lg p-6 text-center text-gray-500">
              Select a class to view details
            </div>
          )}
        </div>
      </div>

      {/* Namespaces Section */}
      <div className="mt-8 bg-white border border-gray-200 rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Namespaces</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {schema.namespaces.map((ns, idx) => (
            <div key={idx} className="bg-gray-50 p-3 rounded font-mono text-sm break-all">
              {ns}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default RDFSchemaPage;
