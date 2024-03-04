import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'package:mobile/app_model.dart';
import 'package:mobile/formaters.dart';
import 'package:mobile/api.dart';
import 'package:mobile/schemas.dart';
import 'package:mobile/pages/profile/edit_details.dart';

class TrainerProfilePage extends StatefulWidget {
  const TrainerProfilePage({super.key});

  @override
  State<TrainerProfilePage> createState() => _TrainerProfilePageState();
}

class _TrainerProfilePageState extends State<TrainerProfilePage> {
  bool _refresh = false;

  void refresh() {
    setState(() {
      _refresh = !_refresh;
    });
  }

  void uploadCertificateOnPressed() {
    FilePicker.platform.pickFiles().then((FilePickerResult? result) {
      if (result?.files.single.path != null) {
        String filePath = result!.files.single.path!;

        API
            .post(context, '/profile/upload-first-certificate',
                filePath: filePath)
            .then((Response res) {
          API.post(context, '/auth/logout').then((Response res2) {
            Provider.of<AppModel>(context, listen: false).setLogout();
          }).onError((error, stackTrace) {
            Provider.of<AppModel>(context, listen: false).setLogout();
          });
        });
      }
    });
  }

  void editProfileOnPressed() {
    UserSchema user = Provider.of<AppModel>(context, listen: false).user!;

    EditDetails.open(context, user, editProfileDialogOnSave);
  }

  void editProfileDialogOnSave(Function closeDialog, String name, String email,
      String phone, String gender, String description) {
    UserSchema user = Provider.of<AppModel>(context, listen: false).user!;

    Map<String, dynamic> params = {};

    if (name != user.name) {
      params["new_name"] = name;
    }

    if (email != user.email) {
      params["new_email"] = email;
    }

    if (phone != user.phone) {
      params["new_phone"] = phone;
    }

    if (gender != user.gender) {
      params["new_gender"] = gender;
    }

    API
        .post(context, '/profile/update-details', params: params)
        .then((Response res) {
      if (res.hasError) {
        closeDialog();
        return;
      }

      UserSchema updatedUser = UserSchema.fromJson(res.data);

      Provider.of<AppModel>(context, listen: false).setUser(updatedUser);

      closeDialog();
    });
  }

  void uploadProfilePictureOnPressed() {
    FilePicker.platform.pickFiles().then((FilePickerResult? result) {
      if (result?.files.single.path != null) {
        String filePath = result!.files.single.path!;

        API
            .post(context, '/profile/upload-profile-picture',
                filePath: filePath)
            .then((Response res) {
          if (res.hasError) {
            return;
          }

          refresh();
        });
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    UserSchema user = Provider.of<AppModel>(context).user!;

    String authToken = Provider.of<AppModel>(context).authToken!;

    String imageUrl =
        '${API.getURL('/profile/get-profile-picture', authToken)}&now=${DateTime.now().millisecondsSinceEpoch.toString()}';

    int age = calculateAge(user.dateOfBirth);

    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Profile',
          style: TextStyle(
            color: Colors.white,
            letterSpacing: 2.0,
          ),
        ),
        centerTitle: true,
        backgroundColor: Colors.grey[800],
        elevation: 0.0,
      ),
      body: Padding(
        padding: const EdgeInsets.fromLTRB(30.0, 40.0, 30.0, 0.0),
        child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              Center(
                child: Stack(
                  children: [
                    CircleAvatar(
                      backgroundImage: NetworkImage(imageUrl),
                      radius: 80.0,
                    ),
                    Positioned(
                      bottom: 0.0,
                      right: 0.0,
                      child: FloatingActionButton(
                        onPressed: uploadProfilePictureOnPressed,
                        mini: true,
                        child: const Icon(Icons.camera_alt_rounded),
                      ),
                    ),
                  ],
                ),
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Text(
                    'Edit Profile',
                    style: TextStyle(
                      color: Colors.black87,
                      letterSpacing: 2.0,
                      fontSize: 14.0,
                    ),
                  ),
                  IconButton(
                      onPressed: editProfileOnPressed,
                      icon: const Icon(Icons.edit))
                ],
              ),
              Divider(
                height: 10.0,
                color: Colors.grey[800],
              ),
              // Each Row contains the code in the first column and an ElevatedButton in the second column
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // First column: Code
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Name',
                        style: TextStyle(
                          color: Colors.black87,
                          letterSpacing: 2.0,
                          fontSize: 16.0,
                        ),
                      ),
                      Text(
                        user.name,
                        style: const TextStyle(
                            color: Colors.black87,
                            letterSpacing: 2.0,
                            fontSize: 16.0,
                            fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                  // Second column: ElevatedButton
                  Column(
                    children: [
                      ElevatedButton(
                        onPressed: uploadCertificateOnPressed,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.white70, // Background color
                          foregroundColor: Colors.black87, // Text color
                          shape: RoundedRectangleBorder(
                            borderRadius:
                                BorderRadius.circular(8), // Rounded corners
                          ),
                          padding: const EdgeInsets.symmetric(
                              vertical: 6, horizontal: 6), // Padding
                        ),
                        child: const Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(Icons.add_box), // Icon
                            SizedBox(width: 4), // Spacing between icon and text
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'Upload certificate',
                                  style: TextStyle(fontSize: 16), // Text style
                                ),
                                Text(
                                  'to become coach',
                                  style: TextStyle(fontSize: 16), // Text style
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              const Text(
                'Personal Details',
                style: TextStyle(
                  color: Colors.black87,
                  letterSpacing: 2.0,
                  fontSize: 16.0,
                ),
              ),
              const SizedBox(
                height: 2.0,
              ),
              Row(
                children: [
                  const Text(
                    'Age:',
                    style: TextStyle(
                      color: Colors.black87,
                      letterSpacing: 2.0,
                      fontSize: 14.0,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    '$age',
                    style: const TextStyle(
                        color: Colors.black87,
                        letterSpacing: 2.0,
                        fontSize: 14.0,
                        fontWeight: FontWeight.bold),
                  ),
                ],
              ),
              Row(
                children: [
                  const Text(
                    'Gender:',
                    style: TextStyle(
                      color: Colors.black87,
                      letterSpacing: 2.0,
                      fontSize: 14.0,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    user.gender,
                    style: const TextStyle(
                        color: Colors.black87,
                        letterSpacing: 2.0,
                        fontSize: 14.0,
                        fontWeight: FontWeight.bold),
                  ),
                ],
              ),
              Divider(
                height: 10.0,
                color: Colors.grey[800],
              ),
              const Text(
                'Contact',
                style: TextStyle(
                  color: Colors.black87,
                  letterSpacing: 2.0,
                  fontSize: 16.0,
                ),
              ),
              const SizedBox(
                height: 10.0,
              ),
              Row(
                children: <Widget>[
                  const Icon(
                    Icons.email,
                    color: Colors.black87,
                    size: 35.0,
                  ),
                  const SizedBox(
                    width: 2.0,
                  ),
                  const Text(
                    'Email', // Change to user.email or appropriate data
                    style: TextStyle(
                      color: Colors.black87,
                      fontSize: 18.0,
                      letterSpacing: 1.0,
                    ),
                  ),
                  const SizedBox(
                    width: 3.0,
                  ),
                  Text(
                    user.email,
                    style: const TextStyle(
                        color: Colors.black87,
                        letterSpacing: 2.0,
                        fontSize: 14.0,
                        fontWeight: FontWeight.bold),
                  ),
                ],
              ),
              const SizedBox(
                height: 10.0,
              ),
              Row(
                children: <Widget>[
                  const Icon(
                    Icons.phone,
                    color: Colors.black87,
                    size: 35.0,
                  ),
                  const SizedBox(
                    width: 2.0,
                  ),
                  const Text(
                    'Phone', // Change to user.phone or appropriate data
                    style: TextStyle(
                      color: Colors.black87,
                      fontSize: 18.0,
                      letterSpacing: 1.0,
                    ),
                  ),
                  const SizedBox(
                    width: 3.0,
                  ),
                  Text(
                    user.phone,
                    style: const TextStyle(
                        color: Colors.black87,
                        letterSpacing: 2.0,
                        fontSize: 14.0,
                        fontWeight: FontWeight.bold),
                  ),
                ],
              ),
            ]),
      ),
    ); //scaffold
  }
}
