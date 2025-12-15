# Flutter Mobile Integration Guide

This guide explains how to integrate the EcoCash Assistant Next.js UI into your Flutter mobile app using WebView with JavaScript bridge communication.

## Overview

The EcoCash Assistant UI is embedded in a Flutter WebView and communicates with the native app via JavaScript's `postMessage` API. This enables:

- **JWT Authentication**: Pass JWT tokens from Flutter to the WebView
- **Context Passing**: Send transaction context and metadata
- **Deep Linking**: Handle navigation requests from the UI back to native app

## Architecture

```
Flutter App
  └── WebView (EcoCash Assistant UI)
       ├── Receives: JWT token, context via postMessage
       └── Sends: Navigation requests via postMessage
```

## Prerequisites

- Flutter app with `webview_flutter` package
- EcoCash Assistant frontend deployed (or running locally)
- JWT token generation/management in Flutter app

## Setup

### 1. Add Dependencies

Add `webview_flutter` to your `pubspec.yaml`:

```yaml
dependencies:
  flutter:
    sdk: flutter
  webview_flutter: ^4.4.2
```

### 2. Create WebView Widget

Create a widget to host the EcoCash Assistant:

```dart
import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';

class EcoCashAssistantScreen extends StatefulWidget {
  final String jwtToken;
  final String? userId;
  final Map<String, dynamic>? initialContext;
  
  const EcoCashAssistantScreen({
    Key? key,
    required this.jwtToken,
    this.userId,
    this.initialContext,
  }) : super(key: key);

  @override
  State<EcoCashAssistantScreen> createState() => _EcoCashAssistantScreenState();
}

class _EcoCashAssistantScreenState extends State<EcoCashAssistantScreen> {
  late final WebViewController _controller;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _initializeWebView();
  }

  void _initializeWebView() {
    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setNavigationDelegate(
        NavigationDelegate(
          onPageFinished: (String url) {
            setState(() {
              _isLoading = false;
            });
            // Send JWT token and context after page loads
            _sendTokenToWebView();
            if (widget.initialContext != null) {
              _sendContextToWebView();
            }
          },
        ),
      )
      ..addJavaScriptChannel(
        'FlutterBridge',
        onMessageReceived: (JavaScriptMessage message) {
          _handleMessageFromWebView(message.message);
        },
      )
      ..loadRequest(
        Uri.parse('https://your-ecocash-assistant-domain.com'), // Replace with your URL
      );
  }

  void _sendTokenToWebView() {
    final script = '''
      window.postMessage({
        type: 'SET_TOKEN',
        token: '${widget.jwtToken}',
        userId: '${widget.userId ?? 'demo_user'}',
        timestamp: Date.now()
      }, '*');
    ''';
    _controller.runJavaScript(script);
  }

  void _sendContextToWebView() {
    final contextJson = jsonEncode(widget.initialContext);
    final script = '''
      window.postMessage({
        type: 'SET_CONTEXT',
        context: $contextJson,
        timestamp: Date.now()
      }, '*');
    ''';
    _controller.runJavaScript(script);
  }

  void _handleMessageFromWebView(String message) {
    try {
      final data = jsonDecode(message);
      final type = data['type'];
      
      switch (type) {
        case 'NAVIGATE':
          _handleNavigation(data['route'], data['params']);
          break;
        case 'ERROR':
          print('Error from WebView: ${data['message']}');
          break;
        default:
          print('Unknown message type: $type');
      }
    } catch (e) {
      print('Error parsing message from WebView: $e');
    }
  }

  void _handleNavigation(String? route, Map<String, dynamic>? params) {
    // Handle navigation requests from WebView
    // Example: Navigate to transaction details screen
    if (route == 'transaction_details' && params != null) {
      final transactionId = params['transactionId'];
      // Navigate to transaction details screen
      Navigator.pushNamed(
        context,
        '/transaction-details',
        arguments: transactionId,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('EcoCash Assistant'),
      ),
      body: Stack(
        children: [
          WebViewWidget(controller: _controller),
          if (_isLoading)
            const Center(
              child: CircularProgressIndicator(),
            ),
        ],
      ),
    );
  }
}
```

### 3. Usage Examples

#### Basic Usage (Just JWT)

```dart
Navigator.push(
  context,
  MaterialPageRoute(
    builder: (context) => EcoCashAssistantScreen(
      jwtToken: 'your-jwt-token-here',
      userId: 'user_12345',
    ),
  ),
);
```

#### With Transaction Help Context

When user clicks "Get Help" from a transaction page:

```dart
Navigator.push(
  context,
  MaterialPageRoute(
    builder: (context) => EcoCashAssistantScreen(
      jwtToken: 'your-jwt-token-here',
      userId: 'user_12345',
      initialContext: {
        'transactionId': 'txn_12345',
        'merchant': 'Coffee Shop',
        'amount': 50.0,
        'date': '2025-01-15',
      },
    ),
  ),
);
```

Then trigger the transaction help flow:

```dart
// After WebView loads, send transaction help message
void _triggerTransactionHelp(String transactionId) {
  final script = '''
    window.postMessage({
      type: 'TRANSACTION_HELP',
      transactionId: '$transactionId',
      timestamp: Date.now()
    }, '*');
  ''';
  _controller.runJavaScript(script);
}
```

## Message Protocol

### Messages from Flutter to WebView

#### SET_TOKEN
```javascript
{
  type: 'SET_TOKEN',
  token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
  userId: 'user_12345',
  timestamp: 1234567890
}
```

#### SET_CONTEXT
```javascript
{
  type: 'SET_CONTEXT',
  context: {
    deviceInfo: {
      platform: 'android',
      device: 'Pixel 6',
      app_version: '2.5.0'
    },
    channel: 'mobile'
  },
  timestamp: 1234567890
}
```

#### TRANSACTION_HELP
```javascript
{
  type: 'TRANSACTION_HELP',
  transactionId: 'txn_12345',
  timestamp: 1234567890
}
```

### Messages from WebView to Flutter

#### NAVIGATE
```javascript
{
  type: 'NAVIGATE',
  route: 'transaction_details',
  params: {
    transactionId: 'txn_12345'
  }
}
```

#### ERROR
```javascript
{
  type: 'ERROR',
  message: 'Error description',
  code: 'ERROR_CODE'
}
```

## Security Considerations

### 1. JWT Token Storage

- **Never store JWT tokens in plain text**
- Use Flutter's secure storage (e.g., `flutter_secure_storage`)
- Generate short-lived tokens (15-30 minutes)
- Implement token refresh mechanism

```dart
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

final storage = FlutterSecureStorage();

// Store token
await storage.write(key: 'jwt_token', value: token);

// Retrieve token
final token = await storage.read(key: 'jwt_token');
```

### 2. HTTPS Only

- Always use HTTPS for the WebView URL
- Never load the assistant over HTTP in production
- Validate SSL certificates

### 3. Origin Validation

The WebView validates message origins. In production, ensure your Flutter app's origin is whitelisted in `frontend/lib/mobile-bridge.ts`.

### 4. Token Expiry Handling

Handle token expiry gracefully:

```dart
void _handleTokenExpiry() {
  // Refresh token
  final newToken = await refreshJWTToken();
  
  // Send new token to WebView
  final script = '''
    window.postMessage({
      type: 'SET_TOKEN',
      token: '$newToken',
      userId: '${widget.userId}',
      timestamp: Date.now()
    }, '*');
  ''';
  _controller.runJavaScript(script);
}
```

## Error Handling

### Network Errors

```dart
_controller.setNavigationDelegate(
  NavigationDelegate(
    onHttpError: (HttpResponseError error) {
      print('HTTP Error: ${error.response?.statusCode}');
      // Show error message to user
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to load assistant')),
      );
    },
    onWebResourceError: (WebResourceError error) {
      print('Web Resource Error: ${error.description}');
    },
  ),
);
```

### JavaScript Errors

Monitor JavaScript console for errors:

```dart
_controller.addJavaScriptChannel(
  'Console',
  onMessageReceived: (JavaScriptMessage message) {
    print('JS Console: ${message.message}');
  },
);
```

## Testing

### Using the HTML Test Wrapper

Before integrating with Flutter, test the WebView communication using the HTML test wrapper:

1. Open `frontend/public/mobile-wrapper.html` in a browser
2. Use the UI controls to send JWT tokens and context
3. Verify the EcoCash Assistant receives and processes messages correctly

### Flutter Testing

1. **Unit Tests**: Test message serialization/deserialization
2. **Widget Tests**: Test WebView widget initialization
3. **Integration Tests**: Test full flow with mock JWT tokens

## Best Practices

1. **Lazy Loading**: Only load the WebView when user opens the assistant
2. **Caching**: Cache the WebView URL to improve load times
3. **Offline Handling**: Show appropriate message when offline
4. **Loading States**: Show loading indicator while WebView initializes
5. **Error Recovery**: Implement retry mechanism for failed loads

## Troubleshooting

### WebView Not Loading

- Check network connectivity
- Verify URL is correct and accessible
- Check CORS settings on backend
- Ensure HTTPS is used in production

### Messages Not Received

- Verify JavaScript is enabled in WebView
- Check message format matches protocol
- Ensure `postMessage` is called after page load
- Check browser console for errors

### JWT Not Working

- Verify token format is correct
- Check token hasn't expired
- Ensure token is sent after WebView loads
- Check backend logs for authentication errors

## Example: Complete Integration

```dart
// In your transaction details screen
class TransactionDetailsScreen extends StatelessWidget {
  final String transactionId;
  
  void _openAssistant(BuildContext context) async {
    // Get JWT token from secure storage
    final storage = FlutterSecureStorage();
    final token = await storage.read(key: 'jwt_token');
    
    if (token == null) {
      // Handle missing token
      return;
    }
    
    // Navigate to assistant with transaction context
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => EcoCashAssistantScreen(
          jwtToken: token,
          userId: await _getUserId(),
          initialContext: {
            'transactionId': transactionId,
          },
        ),
      ),
    );
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Transaction Details')),
      body: Column(
        children: [
          // Transaction details UI
          ElevatedButton(
            onPressed: () => _openAssistant(context),
            child: Text('Get Help'),
          ),
        ],
      ),
    );
  }
}
```

## Support

For issues or questions:
- Check the [EcoCash Assistant README](../README.md)
- Review the [Architecture Documentation](../docs/architecture.md)
- Open an issue on the repository

