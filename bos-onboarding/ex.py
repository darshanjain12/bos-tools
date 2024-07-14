abc=[{'dbo.section': 'Buildings', 'dbo.entity_name': 'UK-LON-BLDNG1', 'dbo.type': 'FACILITIES/BUILDING', 'dbo.id': '3654fc48-914e-4a55-82f6-126534244886', 'dbo.connections.contains': ''}, {'dbo.section': 'Floors', 'dbo.entity_name': 'UK-LON-BLDNG1_FL1', 'dbo.type': 'FACILITIES/FLOOR', 'dbo.id': 'a388563d-58e3-4534-b133-19389f6650a4', 'dbo.connections.contains': 'UK-LON-BLDNG1'}, {'dbo.section': 'Rooms', 'dbo.entity_name': 'UK-LON-BLDNG1_RM1', 'dbo.type': 'FACILITIES/ROOM', 'dbo.id': 'b9f2c8b8-d67e-4b50-824a-7b48ff877429', 'dbo.connections.contains': 'UK-LON-BLDNG1-FL1'}, {'dbo.section': 'Zones', 'dbo.entity_name': 'UK-LON-BLDNG1_ZN1', 'dbo.type': 'HVAC/ZONE', 'dbo.id': 'a0f68db4-f074-49cf-8e80-d65634587f9f', 'dbo.connections.contains': 'UK-LON-BLDNG1-RM1'}, {'dbo.section': 'Rooms', 'dbo.entity_name': 'UK-LON-BLDNG1_RM2', 'dbo.type': 'FACILITIES/ROOM', 'dbo.id': '58d709a5-aa50-4134-a035-0ccc2d01fd48', 'dbo.connections.contains': 'UK-LON-BLDNG1_FL1'}, {'dbo.section': 'Zones', 'dbo.entity_name': 'UK-LON-BLDNG1_ZN2', 'dbo.type': 'HVAC/ZONE', 'dbo.id': 'bdf2e667-8ab2-4ae3-bcc9-9c6c7d995535', 'dbo.connections.contains': 'UK-LON-BLDNG1_RM2'}]
b={}
for i in abc:
    b[i['dbo.entity_name']]=i['dbo.id']

print(b)

if 'UK-LON-BLDNG1' in b:
    print(b['UK-LON-BLDNG1'])
    print(True)

else: 
    print(False)


print({'a': 1,'a':2})