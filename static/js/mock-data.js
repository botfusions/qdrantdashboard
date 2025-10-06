// Mock data for testing when Qdrant is not accessible

const MOCK_DATA = {
    enabled: false, // Set to false when Qdrant is accessible

    status: {
        status: "online",
        data: {
            title: "qdrant",
            version: "1.7.4"
        }
    },

    collections: {
        result: {
            collections: [
                {
                    name: "legal_documents",
                    vectors_count: 15420,
                    config: {
                        params: {
                            vectors: {
                                size: 1536,
                                distance: "Cosine"
                            }
                        }
                    }
                },
                {
                    name: "court_decisions",
                    vectors_count: 8934,
                    config: {
                        params: {
                            vectors: {
                                size: 768,
                                distance: "Cosine"
                            }
                        }
                    }
                },
                {
                    name: "legislation",
                    vectors_count: 5621,
                    config: {
                        params: {
                            vectors: {
                                size: 1536,
                                distance: "Cosine"
                            }
                        }
                    }
                }
            ]
        }
    },

    cluster: {
        result: {
            peer_id: "demo-peer-001",
            raft_info: {
                role: "Leader"
            },
            status: "Enabled"
        }
    },

    telemetry: {
        result: {
            app: {
                status: "running",
                memory_usage: 524288000, // ~500 MB
                version: "1.7.4"
            },
            collections: [
                { name: "legal_documents", vectors_count: 15420 },
                { name: "court_decisions", vectors_count: 8934 },
                { name: "legislation", vectors_count: 5621 }
            ]
        }
    }
};

// Override fetch functions to use mock data
if (MOCK_DATA.enabled) {
    console.log('[MOCK] Using mock data for Qdrant API');

    const originalFetch = window.fetch;
    window.fetch = function(url, options) {
        // Check if it's a Qdrant API call
        if (typeof url === 'string' && url.includes('/api/qdrant/')) {
            console.log('[MOCK] Intercepted:', url);

            if (url.includes('/status')) {
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve(MOCK_DATA.status)
                });
            }

            if (url.includes('/collections') && !url.includes('/points')) {
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve(MOCK_DATA.collections)
                });
            }

            if (url.includes('/cluster')) {
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve(MOCK_DATA.cluster)
                });
            }

            if (url.includes('/telemetry')) {
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve(MOCK_DATA.telemetry)
                });
            }
        }

        // Call original fetch for other requests
        return originalFetch.call(this, url, options);
    };
}
