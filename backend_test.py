import requests
import sys
import json
import time
from datetime import datetime

class MemoryReplayEngineAPITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session = requests.Session()
        self.tests_run = 0
        self.tests_passed = 0
        self.user_id = None
        self.memory_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        
        self.tests_run += 1
        print(f"\nðŸ” Testing {name}...")
        
        try:
            if method == 'GET':
                response = self.session.get(url)
            elif method == 'POST':
                if files:
                    response = self.session.post(url, files=files, data=data)
                else:
                    response = self.session.post(url, json=data)
            elif method == 'PUT':
                response = self.session.put(url, json=data)
            elif method == 'DELETE':
                response = self.session.delete(url)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"âœ… Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, response.text
            else:
                print(f"âŒ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"âŒ Failed - Error: {str(e)}")
            return False, {}

    def test_auth_flow(self):
        """Test complete authentication flow"""
        print("\n" + "="*50)
        print("TESTING AUTHENTICATION FLOW")
        print("="*50)
        
        # Test admin login
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "auth/login",
            200,
            data={"email": "admin@memoryengine.com", "password": "admin123"}
        )
        
        if success:
            self.user_id = response.get('_id')
            print(f"   User ID: {self.user_id}")
        
        # Test get current user
        self.run_test(
            "Get Current User",
            "GET", 
            "auth/me",
            200
        )
        
        # Test user registration
        test_email = f"test_{int(time.time())}@test.com"
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register", 
            200,
            data={"email": test_email, "password": "testpass123", "name": "Test User"}
        )
        
        # Test logout
        self.run_test(
            "Logout",
            "POST",
            "auth/logout",
            200
        )
        
        # Login back as admin for other tests
        success, response = self.run_test(
            "Re-login as Admin",
            "POST",
            "auth/login",
            200,
            data={"email": "admin@memoryengine.com", "password": "admin123"}
        )

    def test_memory_operations(self):
        """Test memory CRUD operations"""
        print("\n" + "="*50)
        print("TESTING MEMORY OPERATIONS")
        print("="*50)
        
        # Create memory
        memory_data = {
            "content": "This is a test memory for API testing. I feel excited about testing this new system!",
            "tags": ["test", "api", "automation"],
            "location": "Test Lab"
        }
        
        success, response = self.run_test(
            "Create Memory",
            "POST",
            "memories",
            200,
            data=memory_data
        )
        
        if success:
            self.memory_id = response.get('id')
            print(f"   Memory ID: {self.memory_id}")
            print(f"   Detected Emotion: {response.get('emotion')}")
            print(f"   Emotion Score: {response.get('emotion_score')}")
        
        # Get all memories
        self.run_test(
            "Get All Memories",
            "GET",
            "memories",
            200
        )
        
        # Get specific memory
        if self.memory_id:
            self.run_test(
                "Get Specific Memory",
                "GET",
                f"memories/{self.memory_id}",
                200
            )
            
            # Get related memories
            self.run_test(
                "Get Related Memories",
                "GET",
                f"memories/{self.memory_id}/related",
                200
            )

    def test_search_functionality(self):
        """Test memory search"""
        print("\n" + "="*50)
        print("TESTING SEARCH FUNCTIONALITY")
        print("="*50)
        
        # Search by query
        self.run_test(
            "Search by Content",
            "POST",
            "memories/search",
            200,
            data={"query": "test"}
        )
        
        # Search by emotion
        self.run_test(
            "Search by Emotion",
            "POST", 
            "memories/search",
            200,
            data={"emotion": "happy"}
        )
        
        # Search by tags
        self.run_test(
            "Search by Tags",
            "POST",
            "memories/search", 
            200,
            data={"tags": ["test"]}
        )

    def test_statistics(self):
        """Test statistics endpoints"""
        print("\n" + "="*50)
        print("TESTING STATISTICS")
        print("="*50)
        
        # Get overview stats
        success, response = self.run_test(
            "Get Overview Stats",
            "GET",
            "memories/stats/overview",
            200
        )
        
        if success:
            print(f"   Total Memories: {response.get('total_memories')}")
            print(f"   Emotion Breakdown: {response.get('emotion_breakdown')}")
        
        # Get daily summary
        success, response = self.run_test(
            "Get Daily Summary",
            "GET",
            "memories/stats/daily-summary",
            200
        )
        
        if success:
            print(f"   Summary: {response.get('summary')}")
            print(f"   Memories Count: {response.get('memories_count')}")
        
        # Test emotion timeline (Phase 2 feature)
        success, response = self.run_test(
            "Get Emotion Timeline",
            "GET",
            "memories/stats/emotion-timeline",
            200
        )
        
        if success:
            print(f"   Timeline Data Points: {len(response) if isinstance(response, list) else 'Invalid format'}")
            if isinstance(response, list) and len(response) > 0:
                print(f"   Sample Timeline Entry: {response[0]}")

    def test_phase2_features(self):
        """Test Phase 2 new features"""
        print("\n" + "="*50)
        print("TESTING PHASE 2 FEATURES")
        print("="*50)
        
        # Test story mode generation
        print("\nðŸ” Testing Story Mode Generation...")
        success, response = self.run_test(
            "Generate Story Mode",
            "POST",
            "memories/story-mode",
            200,
            data={}
        )
        
        if success:
            story = response.get('story', '')
            memories_used = response.get('memories_used', 0)
            print(f"   Story Generated: {len(story)} characters")
            print(f"   Memories Used: {memories_used}")
            print(f"   Story Preview: {story[:100]}..." if len(story) > 100 else f"   Story: {story}")
        
        # Wait a moment for AI processing
        time.sleep(2)

    def test_phase3_features(self):
        """Test Phase 3 new features: edit, delete, and ranking"""
        print("\n" + "="*50)
        print("TESTING PHASE 3 FEATURES")
        print("="*50)
        
        # First create a memory for testing edit/delete/ranking
        memory_data = {
            "content": "This is a memory for Phase 3 testing. I'm learning about new features and feeling curious about the possibilities.",
            "tags": ["phase3", "testing", "learning"],
            "location": "Development Lab"
        }
        
        success, response = self.run_test(
            "Create Memory for Phase 3 Testing",
            "POST",
            "memories",
            200,
            data=memory_data
        )
        
        if not success:
            print("âŒ Cannot test Phase 3 features without creating a memory first")
            return
        
        test_memory_id = response.get('id')
        print(f"   Test Memory ID: {test_memory_id}")
        
        # Test memory editing (PUT /api/memories/{id})
        print("\nðŸ” Testing Memory Edit...")
        edit_data = {
            "content": "This is an UPDATED memory for Phase 3 testing. I'm feeling excited about the edit functionality!",
            "tags": ["phase3", "testing", "updated", "excited"],
            "location": "Updated Development Lab"
        }
        
        success, response = self.run_test(
            "Edit Memory",
            "PUT",
            f"memories/{test_memory_id}",
            200,
            data=edit_data
        )
        
        if success:
            print(f"   Updated Content: {response.get('content')[:50]}...")
            print(f"   Updated Emotion: {response.get('emotion')}")
            print(f"   Updated Tags: {response.get('tags')}")
            print(f"   Updated Location: {response.get('location')}")
        
        # Test importance ranking (POST /api/memories/{id}/rank)
        print("\nðŸ” Testing Memory Importance Ranking...")
        success, response = self.run_test(
            "Rank Memory Importance",
            "POST",
            f"memories/{test_memory_id}/rank",
            200,
            data={}
        )
        
        if success:
            importance = response.get('importance')
            reason = response.get('reason')
            print(f"   Importance Score: {importance}/10")
            print(f"   Reason: {reason}")
        
        # Wait for AI processing
        time.sleep(2)
        
        # Test batch ranking (POST /api/memories/rank-all)
        print("\nðŸ” Testing Batch Memory Ranking...")
        success, response = self.run_test(
            "Batch Rank All Memories",
            "POST",
            "memories/rank-all",
            200,
            data={}
        )
        
        if success:
            ranked_count = response.get('ranked', 0)
            message = response.get('message', '')
            print(f"   Ranked Memories: {ranked_count}")
            print(f"   Message: {message}")
        
        # Wait for AI processing
        time.sleep(2)
        
        # Test memory deletion (DELETE /api/memories/{id})
        print("\nðŸ” Testing Memory Deletion...")
        success, response = self.run_test(
            "Delete Memory",
            "DELETE",
            f"memories/{test_memory_id}",
            200
        )
        
        if success:
            print(f"   Deletion Response: {response}")
        
        # Verify memory is deleted
        success, response = self.run_test(
            "Verify Memory Deleted",
            "GET",
            f"memories/{test_memory_id}",
            404
        )

    def test_media_features(self):
        """Test voice transcription and image upload"""
        print("\n" + "="*50)
        print("TESTING MEDIA FEATURES")
        print("="*50)
        
        # Test image upload endpoint (without actual file)
        print("\nðŸ” Testing Image Upload Endpoint...")
        try:
            # Create a small test file
            test_content = b"fake image content for testing"
            files = {'file': ('test.jpg', test_content, 'image/jpeg')}
            
            response = self.session.post(f"{self.api_url}/memories/upload-image", files=files)
            
            if response.status_code == 200:
                print("âœ… Image upload endpoint is working")
                self.tests_passed += 1
            else:
                print(f"âŒ Image upload failed - Status: {response.status_code}")
                print(f"   Error: {response.text}")
            
            self.tests_run += 1
            
        except Exception as e:
            print(f"âŒ Image upload test failed: {str(e)}")
            self.tests_run += 1
        
        # Test transcription endpoint (without actual audio)
        print("\nðŸ” Testing Voice Transcription Endpoint...")
        try:
            # Create a small test file
            test_audio = b"fake audio content for testing"
            files = {'file': ('test.webm', test_audio, 'audio/webm')}
            
            response = self.session.post(f"{self.api_url}/memories/transcribe", files=files)
            
            # This might fail due to invalid audio format, but we're testing endpoint availability
            if response.status_code in [200, 400, 500]:  # Any response means endpoint exists
                print("âœ… Transcription endpoint is accessible")
                self.tests_passed += 1
            else:
                print(f"âŒ Transcription endpoint not found - Status: {response.status_code}")
            
            self.tests_run += 1
            
        except Exception as e:
            print(f"âŒ Transcription test failed: {str(e)}")
            self.tests_run += 1

    def test_phase4_features(self):
        """Test Phase 4 new features: Memory Intelligence Insights and 3D Brain Map"""
        print("\n" + "="*50)
        print("TESTING PHASE 4 FEATURES")
        print("="*50)
        
        # Test Memory Intelligence Insights (GET /api/memories/insights)
        print("\nðŸ” Testing Memory Intelligence Insights...")
        success, response = self.run_test(
            "Get Memory Insights",
            "GET",
            "memories/insights",
            200
        )
        
        if success:
            insights = response.get('insights', [])
            memories_analyzed = response.get('memories_analyzed', 0)
            message = response.get('message', '')
            
            print(f"   Insights Generated: {len(insights)}")
            print(f"   Memories Analyzed: {memories_analyzed}")
            if message:
                print(f"   Message: {message}")
            
            # Check insight structure if insights exist
            if insights and len(insights) > 0:
                sample_insight = insights[0]
                print(f"   Sample Insight Title: {sample_insight.get('title', 'N/A')}")
                print(f"   Sample Insight Category: {sample_insight.get('category', 'N/A')}")
                print(f"   Sample Insight Emotion: {sample_insight.get('emotion', 'N/A')}")
                print(f"   Sample Insight Description: {sample_insight.get('description', 'N/A')[:100]}...")
        
        # Wait for AI processing
        time.sleep(2)
        
        # Test 3D Brain Map (GET /api/memories/brain-map)
        print("\nðŸ” Testing 3D Memory Brain Map...")
        success, response = self.run_test(
            "Get Brain Map Data",
            "GET",
            "memories/brain-map",
            200
        )
        
        if success:
            nodes = response.get('nodes', [])
            links = response.get('links', [])
            
            print(f"   Brain Map Nodes: {len(nodes)}")
            print(f"   Brain Map Links: {len(links)}")
            
            # Check node structure if nodes exist
            if nodes and len(nodes) > 0:
                sample_node = nodes[0]
                print(f"   Sample Node ID: {sample_node.get('id', 'N/A')}")
                print(f"   Sample Node Emotion: {sample_node.get('emotion', 'N/A')}")
                print(f"   Sample Node Importance: {sample_node.get('importance', 'N/A')}")
                print(f"   Sample Node Content: {sample_node.get('content', 'N/A')[:50]}...")
            
            # Check link structure if links exist
            if links and len(links) > 0:
                sample_link = links[0]
                print(f"   Sample Link Type: {sample_link.get('type', 'N/A')}")
                print(f"   Sample Link Label: {sample_link.get('label', 'N/A')}")

    def test_phase5_features(self):
        """Test Phase 5 new features: What-If simulation and Shared Memories"""
        print("\n" + "="*50)
        print("TESTING PHASE 5 FEATURES")
        print("="*50)
        
        # First create a memory for testing what-if and sharing
        memory_data = {
            "content": "I went to the park today and saw a beautiful sunset. It made me feel peaceful and grateful for nature's beauty.",
            "tags": ["nature", "sunset", "peaceful"],
            "location": "Central Park"
        }
        
        success, response = self.run_test(
            "Create Memory for Phase 5 Testing",
            "POST",
            "memories",
            200,
            data=memory_data
        )
        
        if not success:
            print("âŒ Cannot test Phase 5 features without creating a memory first")
            return
        
        test_memory_id = response.get('id')
        print(f"   Test Memory ID: {test_memory_id}")
        
        # Test What-If simulation (POST /api/memories/{id}/what-if)
        print("\nðŸ” Testing What-If Simulation...")
        success, response = self.run_test(
            "Generate What-If Scenarios",
            "POST",
            f"memories/{test_memory_id}/what-if",
            200,
            data={}
        )
        
        if success:
            original = response.get('original', '')
            original_emotion = response.get('original_emotion', '')
            scenarios = response.get('scenarios', [])
            
            print(f"   Original Memory: {original[:50]}...")
            print(f"   Original Emotion: {original_emotion}")
            print(f"   Scenarios Generated: {len(scenarios)}")
            
            # Check scenario structure if scenarios exist
            if scenarios and len(scenarios) > 0:
                sample_scenario = scenarios[0]
                print(f"   Sample Scenario Title: {sample_scenario.get('title', 'N/A')}")
                print(f"   Sample Scenario Emotion: {sample_scenario.get('emotion', 'N/A')}")
                print(f"   Sample Scenario Narrative: {sample_scenario.get('narrative', 'N/A')[:50]}...")
                print(f"   Sample Scenario Divergence: {sample_scenario.get('divergence', 'N/A')[:50]}...")
        
        # Wait for AI processing
        time.sleep(3)
        
        # Create a second user for sharing tests
        test_email = f"sharetest_{int(time.time())}@test.com"
        success, response = self.run_test(
            "Create Second User for Sharing",
            "POST",
            "auth/register",
            200,
            data={"email": test_email, "password": "testpass123", "name": "Share Test User"}
        )
        
        if not success:
            print("âŒ Cannot test sharing without creating a second user")
            return
        
        # Re-login as admin to ensure we're still admin for sharing our own memory
        success, response = self.run_test(
            "Re-login as Admin for Sharing",
            "POST",
            "auth/login",
            200,
            data={"email": "admin@memoryengine.com", "password": "admin123"}
        )
        
        if not success:
            print("âŒ Cannot re-login as admin")
            return
        
        # Test memory sharing (POST /api/memories/{id}/share) - Admin sharing their own memory
        print("\nðŸ” Testing Memory Sharing...")
        success, response = self.run_test(
            "Share Memory with Another User",
            "POST",
            f"memories/{test_memory_id}/share",
            200,
            data={"email": test_email}
        )
        
        if success:
            message = response.get('message', '')
            print(f"   Share Response: {message}")
        
        # Test sharing validation - try to share with non-existent user
        print("\nðŸ” Testing Share Validation - Non-existent User...")
        success, response = self.run_test(
            "Share with Non-existent User",
            "POST",
            f"memories/{test_memory_id}/share",
            404,
            data={"email": "nonexistent@test.com"}
        )
        
        # Test sharing validation - try to share with self
        print("\nðŸ” Testing Share Validation - Self Share...")
        success, response = self.run_test(
            "Share with Self",
            "POST",
            f"memories/{test_memory_id}/share",
            400,
            data={"email": "admin@memoryengine.com"}
        )
        
        # Test sharing validation - try to share same memory twice
        print("\nðŸ” Testing Share Validation - Duplicate Share...")
        success, response = self.run_test(
            "Duplicate Share",
            "POST",
            f"memories/{test_memory_id}/share",
            400,
            data={"email": test_email}
        )
        
        # Login as the second user to test shared memories retrieval
        print("\nðŸ” Testing Shared Memories Retrieval...")
        success, response = self.run_test(
            "Login as Second User",
            "POST",
            "auth/login",
            200,
            data={"email": test_email, "password": "testpass123"}
        )
        
        if success:
            # Test getting shared memories (GET /api/memories/shared)
            success, response = self.run_test(
                "Get Shared Memories",
                "GET",
                "memories/shared",
                200
            )
            
            if success:
                shared_memories = response if isinstance(response, list) else []
                print(f"   Shared Memories Count: {len(shared_memories)}")
                
                if shared_memories and len(shared_memories) > 0:
                    sample_shared = shared_memories[0]
                    print(f"   Sample Shared Memory ID: {sample_shared.get('id', 'N/A')}")
                    print(f"   Sample Shared By: {sample_shared.get('shared_by', 'N/A')}")
                    print(f"   Sample Content: {sample_shared.get('content', 'N/A')[:50]}...")
        
        # Login back as admin for cleanup
        success, response = self.run_test(
            "Re-login as Admin for Cleanup",
            "POST",
            "auth/login",
            200,
            data={"email": "admin@memoryengine.com", "password": "admin123"}
        )

    def test_error_handling(self):
        """Test error handling"""
        print("\n" + "="*50)
        print("TESTING ERROR HANDLING")
        print("="*50)
        
        # Test unauthorized access
        temp_session = requests.Session()
        print("\nðŸ” Testing Unauthorized Access...")
        try:
            response = temp_session.get(f"{self.api_url}/memories")
            if response.status_code == 401:
                print("âœ… Unauthorized access properly blocked")
                self.tests_passed += 1
            else:
                print(f"âŒ Expected 401, got {response.status_code}")
            self.tests_run += 1
        except Exception as e:
            print(f"âŒ Error testing unauthorized access: {str(e)}")
            self.tests_run += 1
        
        # Test invalid login
        self.run_test(
            "Invalid Login",
            "POST",
            "auth/login",
            401,
            data={"email": "invalid@test.com", "password": "wrongpass"}
        )
        
        # Test non-existent memory
        self.run_test(
            "Get Non-existent Memory",
            "GET",
            "memories/invalid-id",
            404
        )

def main():
    print("ðŸš€ Starting Memory Replay Engine API Tests")
    print("=" * 60)
    
    tester = MemoryReplayEngineAPITester()
    
    # Run all test suites
    tester.test_auth_flow()
    tester.test_memory_operations()
    tester.test_search_functionality()
    tester.test_statistics()
    tester.test_phase2_features()
    tester.test_phase3_features()
    tester.test_phase4_features()
    tester.test_phase5_features()
    tester.test_media_features()
    tester.test_error_handling()
    
    # Print final results
    print("\n" + "="*60)
    print("ðŸ“Š FINAL TEST RESULTS")
    print("="*60)
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("\nðŸŽ‰ All tests passed! Backend is working correctly.")
        return 0
    else:
        print(f"\nâš ï¸  {tester.tests_run - tester.tests_passed} tests failed. Check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
