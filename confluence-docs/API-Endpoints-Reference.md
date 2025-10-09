# API Endpoints Reference - IED Explorer

**Space**: VPAC
**Category**: Technical Reference
**Last Updated**: 2025-01-09

---

## Base URL

```
http://localhost:8000/api
```

All endpoints require authentication via JWT token in the `Authorization` header:

```
Authorization: Bearer <your_jwt_token>
```

---

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/ieds` | List all IEDs with grouping and search |
| GET | `/ieds/tree` | Get children of a specific node in the IED hierarchy |

---

## GET /api/ieds

Get list of IEDs from an SCL file with optional grouping and search filtering.

### Request

**Query Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_id` | integer | Yes | - | SCL file ID to query |
| `group_by` | string | No | `"type"` | Grouping method: `"type"` or `"bay"` |
| `search` | string | No | `""` | Search filter for IED names (case-insensitive) |

**Example Request**:

```bash
curl -X GET "http://localhost:8000/api/ieds?file_id=1&group_by=type&search=BCU" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Response

**Status Code**: 200 OK

**Response Body**:

```json
{
  "group_by": "type",
  "search": "BCU",
  "groups": {
    "BCU": [
      {
        "uri": "http://example.com/SCL#IED_BCU1",
        "name": "POSTE4BUIS1BCU1",
        "type": "BCU",
        "manufacturer": "Siemens",
        "description": "Bay Control Unit 1"
      },
      {
        "uri": "http://example.com/SCL#IED_BCU2",
        "name": "POSTE4BUIS1BCU2",
        "type": "BCU",
        "manufacturer": "ABB",
        "description": null
      }
    ]
  },
  "total_ieds": 2
}
```

**Response Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `group_by` | string | Echo of the grouping method used |
| `search` | string | Echo of the search filter used |
| `groups` | object | IEDs grouped by the specified field |
| `groups.<key>` | array | List of IEDs in this group |
| `groups.<key>[].uri` | string | Unique RDF URI for the IED |
| `groups.<key>[].name` | string | IED name from SCL file |
| `groups.<key>[].type` | string | IED type (BCU, SCU, etc.) |
| `groups.<key>[].manufacturer` | string | Manufacturer name |
| `groups.<key>[].description` | string\|null | Optional description |
| `total_ieds` | integer | Total number of IEDs (across all groups) |

### Error Responses

**404 Not Found** - SCL file doesn't exist:
```json
{
  "detail": "SCL file not found"
}
```

**400 Bad Request** - File not yet uploaded to RDF store:
```json
{
  "detail": "File not yet uploaded to RDF store"
}
```

**500 Internal Server Error** - Query execution failed:
```json
{
  "detail": "Error querying IEDs: <error_message>"
}
```

### SPARQL Query Used (group_by=type)

```sparql
PREFIX iec: <http://iec61850.com/SCL#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT DISTINCT ?ied ?name ?type ?manufacturer ?desc
WHERE {
  ?ied rdf:type iec:IED .
  OPTIONAL { ?ied iec:name ?name }
  OPTIONAL { ?ied iec:type ?type }
  OPTIONAL { ?ied iec:manufacturer ?manufacturer }
  OPTIONAL { ?ied iec:desc ?desc }
  FILTER(CONTAINS(LCASE(?name), LCASE("BCU")))
}
ORDER BY ?type ?name
LIMIT 1000
```

### SPARQL Query Used (group_by=bay)

```sparql
PREFIX iec: <http://iec61850.com/SCL#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT DISTINCT ?ied ?iedName ?type ?manufacturer ?bay ?bayName
WHERE {
  ?ied rdf:type iec:IED .
  ?ied iec:name ?iedName .
  OPTIONAL { ?ied iec:type ?type }
  OPTIONAL { ?ied iec:manufacturer ?manufacturer }

  # Try to find associated bay through LNode references
  OPTIONAL {
    ?lNode iec:iedName ?iedName .
    ?bay iec:hasLNode ?lNode .
    ?bay rdf:type iec:Bay .
    OPTIONAL { ?bay iec:name ?bayName }
  }

  FILTER(CONTAINS(LCASE(?iedName), LCASE("BCU")))
}
ORDER BY ?bayName ?iedName
LIMIT 1000
```

---

## GET /api/ieds/tree

Get children of a specific node in the IED hierarchy. Used for lazy loading of the expandable tree.

### Request

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_id` | integer | Yes | SCL file ID to query |
| `parent_uri` | string | Yes | RDF URI of the parent node (URL encoded) |
| `parent_type` | string | Yes | Type of parent node (see valid types below) |

**Valid Parent Types**:

| Parent Type | Children Type | Description |
|-------------|---------------|-------------|
| `IED` | `AccessPoint` | Top-level communication access points |
| `AccessPoint` | `Server` | IED server instance |
| `Server` | `LDevice` | Logical devices |
| `LDevice` | `LN0`, `LN` | Logical nodes (LN0 is special, LN are regular) |
| `LN0` | `DataSet`, `GSEControl`, `ReportControl`, `SampledValueControl`, `DOI` | Data organization and control blocks |
| `LN` | `DOI`, `Inputs` | Data object instances and external references |
| `DataSet` | `FCDA` | Functional constraint data attributes |
| `Inputs` | `ExtRef` | External references to other IED data |

**Example Request**:

```bash
curl -X GET "http://localhost:8000/api/ieds/tree?file_id=1&parent_uri=http%3A%2F%2Fexample.com%2FSCL%23IED_BCU1&parent_type=IED" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Response

**Status Code**: 200 OK

**Response Body**:

```json
{
  "parent_uri": "http://example.com/SCL#IED_BCU1",
  "parent_type": "IED",
  "children": [
    {
      "uri": "http://example.com/SCL#IED_BCU1_AP_PROCESS",
      "name": "PROCESS_AP",
      "type": "AccessPoint",
      "hasChildren": true
    },
    {
      "uri": "http://example.com/SCL#IED_BCU1_AP_STATION",
      "name": "STATION_AP",
      "type": "AccessPoint",
      "hasChildren": true
    }
  ],
  "count": 2
}
```

**Response Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `parent_uri` | string | Decoded URI of the parent node |
| `parent_type` | string | Type of the parent node |
| `children` | array | List of child nodes |
| `children[].uri` | string | Unique RDF URI for the child |
| `children[].name` | string | Display name of the child |
| `children[].type` | string | Type of the child node |
| `children[].hasChildren` | boolean | Can this child be expanded further? |
| `children[].*` | any | Additional metadata fields specific to node type |
| `count` | integer | Number of children returned |

### Display Name Formatting

The `name` field is formatted differently based on the parent type:

#### Server Children (LDevices)
Format: `{inst} ({ldName})`
- Example: `LDAGSA1 (AgentServerLD)`

#### LDevice Children (Logical Nodes)
Format: `{prefix}{lnClass}{inst}`
- Example: `I01ATCTR11` (prefix=I01A, lnClass=TCTR, inst=11)
- Example: `LPHD0` (prefix=empty, lnClass=LPHD, inst=0)

#### DataSet Children (FCDA)
Format: `{ldInst}.{prefix}{lnClass}{lnInst}.{doName}.{daName} [{fc}]`
- Example: `LDAGSA1.LPHD0.PhyHealth.stVal [ST]`

#### Inputs Children (ExtRef)
Format: `{iedName}/{ldInst}/{prefix}{lnClass}{lnInst}/{doName}/{daName}`
- Example: `POSTE4/LDAGSA1/LPHD0/PhyHealth/stVal`

#### Other Nodes
Format: `{name}` or `{inst}`
- Example: `PROCESS_AP`, `Server`

### hasChildren Logic

Only these node types can be expanded:
- `AccessPoint`
- `Server`
- `LDevice`
- `LN0`
- `LN`
- `DataSet`
- `Inputs`

Leaf nodes (hasChildren=false):
- `DOI` (Data Object Instance)
- `FCDA` (Functional Constraint Data Attribute)
- `ExtRef` (External Reference)
- `GSEControl`, `ReportControl`, `SampledValueControl`

### Error Responses

**404 Not Found** - SCL file doesn't exist:
```json
{
  "detail": "SCL file not found"
}
```

**400 Bad Request** - Invalid parent type:
```json
{
  "detail": "Unknown parent type: InvalidType"
}
```

**500 Internal Server Error** - Query execution failed:
```json
{
  "detail": "Error querying tree: <error_message>"
}
```

### SPARQL Query Examples

#### For IED (get AccessPoints)

```sparql
PREFIX iec: <http://iec61850.com/SCL#>
SELECT ?child ?name ?type
WHERE {
  <http://example.com/SCL#IED_BCU1> iec:hasAccessPoint ?child .
  OPTIONAL { ?child iec:name ?name }
  BIND("AccessPoint" as ?type)
}
```

#### For Server (get LDevices)

```sparql
PREFIX iec: <http://iec61850.com/SCL#>
SELECT ?child ?inst ?ldName ?type
WHERE {
  <http://example.com/SCL#Server1> iec:hasLDevice ?child .
  OPTIONAL { ?child iec:inst ?inst }
  OPTIONAL { ?child iec:ldName ?ldName }
  BIND("LDevice" as ?type)
}
```

#### For LDevice (get Logical Nodes)

```sparql
PREFIX iec: <http://iec61850.com/SCL#>
SELECT ?child ?lnClass ?lnType ?prefix ?inst ?type
WHERE {
  {
    <http://example.com/SCL#LDevice1> iec:hasLN0 ?child .
    BIND("LN0" as ?type)
  } UNION {
    <http://example.com/SCL#LDevice1> iec:hasLN ?child .
    BIND("LN" as ?type)
  }
  OPTIONAL { ?child iec:lnClass ?lnClass }
  OPTIONAL { ?child iec:lnType ?lnType }
  OPTIONAL { ?child iec:prefix ?prefix }
  OPTIONAL { ?child iec:inst ?inst }
}
ORDER BY ?type ?lnClass ?inst
```

#### For LN0 (get DataSets and Controls)

```sparql
PREFIX iec: <http://iec61850.com/SCL#>
SELECT ?child ?name ?type ?category
WHERE {
  {
    <http://example.com/SCL#LN0_1> iec:hasDataSet ?child .
    OPTIONAL { ?child iec:name ?name }
    BIND("DataSet" as ?type)
    BIND("data" as ?category)
  } UNION {
    <http://example.com/SCL#LN0_1> iec:hasGSEControl ?child .
    OPTIONAL { ?child iec:name ?name }
    BIND("GSEControl" as ?type)
    BIND("communication" as ?category)
  } UNION {
    <http://example.com/SCL#LN0_1> iec:hasSampledValueControl ?child .
    OPTIONAL { ?child iec:name ?name }
    BIND("SampledValueControl" as ?type)
    BIND("communication" as ?category)
  } UNION {
    <http://example.com/SCL#LN0_1> iec:hasReportControl ?child .
    OPTIONAL { ?child iec:name ?name }
    BIND("ReportControl" as ?type)
    BIND("communication" as ?category)
  } UNION {
    <http://example.com/SCL#LN0_1> iec:hasDOI ?child .
    OPTIONAL { ?child iec:name ?name }
    BIND("DOI" as ?type)
    BIND("data" as ?category)
  }
}
ORDER BY ?category ?type ?name
```

---

## Authentication

All endpoints require JWT authentication. To obtain a token:

1. **Login**:
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=your_password"
```

2. **Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

3. **Use Token**:
```bash
curl -X GET "http://localhost:8000/api/ieds?file_id=1" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## Rate Limiting

Currently no rate limiting is implemented. In production, consider:
- Rate limiting by IP address
- Rate limiting by user
- Query complexity limits (SPARQL timeout)

---

## Best Practices

1. **Always URL encode parent_uri**: URIs contain special characters
   ```javascript
   const params = new URLSearchParams({
     parent_uri: encodeURIComponent(node.uri)
   });
   ```

2. **Cache tree node children**: Don't re-fetch children that are already loaded
   ```typescript
   if (node.children !== null) {
     // Already loaded, just toggle
     node.isExpanded = !node.isExpanded;
     return;
   }
   ```

3. **Handle errors gracefully**: Show user-friendly messages
   ```typescript
   try {
     const response = await fetch(...);
     if (!response.ok) throw new Error('Failed to fetch');
   } catch (err) {
     setError('Unable to load children. Please try again.');
   }
   ```

4. **Use loading states**: Show spinners while fetching
   ```typescript
   setLoading(true);
   try {
     // ... fetch data
   } finally {
     setLoading(false);
   }
   ```

---

## Related Documentation

- [IED Explorer Overview](./IED-Explorer-Overview.md)
- [SPARQL Query Guide](./SPARQL-Query-Guide.md)
- [Frontend Integration Guide](./Frontend-Integration-Guide.md)

---

**End of API Reference**
