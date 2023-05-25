
INPUT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "$id": "https://example.com/object1684937012.json",
    "title": "Input Schema",
    "type": "object",
    "required": [
        "Records"
    ],
    "properties": {
        "Records": {
            "$id": "#root/Records",
            "title": "Records",
            "type": "array",
            "items": {
                "$id": "#root/Records/items",
                "title": "Items",
                "type": "object",
                "required": [
                    "s3"
                ],
                "properties": {
                    "s3": {
                        "$id": "#root/Records/items/s3",
                        "title": "S3",
                        "type": "object",
                        "required": [
                            "bucket",
                            "object"
                        ],
                        "properties": {
                            "bucket": {
                                "$id": "#root/Records/items/s3/bucket",
                                "title": "Bucket",
                                "type": "object",
                                "required": [
                                    "name"
                                ],
                                "properties": {
                                    "name": {
                                        "$id": "#root/Records/items/s3/bucket/name",
                                        "title": "Name",
                                        "type": "string",
                                        "examples": [
                                            "example-bucket"
                                        ]
                                    }
                                }
                            },
                            "object": {
                                "$id": "#root/Records/items/s3/object",
                                "title": "Object",
                                "type": "object",
                                "required": [
                                    "key"
                                ],
                                "properties": {
                                    "key": {
                                        "$id": "#root/Records/items/s3/object/key",
                                        "title": "Key",
                                        "type": "string",
                                        "examples": [
                                            "test/key"
                                        ]
                                    }
                                }
                            }

                        }
                    }

                }
            }

        }
    }
}

OUTPUT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "$id": "https://example.com/object1684944728.json",
    "title": "Output Schema",
    "type": "object",
    "required": [
        "status",
        "key",
        "content_type"
    ],
    "properties": {
        "status": {
            "$id": "#root/status",
            "title": "Status",
            "type": "string",
            "enum": ["OK", "Error"]
        },
        "key": {
            "$id": "#root/key",
            "title": "Key",
            "type": "string",
            "examples": [
                "sample.txt"
            ]
        },
        "content_type": {
            "$id": "#root/content_type",
            "title": "Content_type",
            "type": "string",
            "examples": [
                "text/plain"
            ]
        }
    }
}
