//  https://github.com/occamLab/ARDataLogger/blob/main/Sources/ARDataLogger/UploadManager.swift
//  UploadManager.swift
//  LidarCane
//
//  Created by Paul Ruvolo on 5/10/21.
//
//  This class manages uploading files to Firebase in a persistent fashion.  It will automatically stop uploading data if not connected to the Internet, can retry multiple times, and persists the list of pending uploads if the app enters the background

import Foundation
import FirebaseStorage
import SWCompression
import FirebaseAuth


/// The upload manager takes care of sending data to Firebase.  Currently we have commented out the section that allows upload jobs to be serialized to local storage: The manager will write the files that should be upload to the phone's local storage if the data cannot be uploaded to Firebase (e.g., if the app enters the background or if the Internet connection drops)
class UploadManager {
    public static let rootFolder: String = "iosLoggerDemo"
    public static var shared = UploadManager()
    
    var files: [TarEntry] = []
    

    /// - Parameters:
    ///   - uploadData: the data to upload
    ///   - contentType: the MIME content type
    ///   - fullPath: the path to the data on the storage bucket
    func putData(_ uploadData: Data, contentType: String, fullPath: String) {
        var info = TarEntryInfo(name: fullPath, type: .regular)
        info.permissions = Permissions.readOwner.union([.writeOwner])
        let tarEntry = TarEntry(info: info, data: uploadData)
        files.append(tarEntry)
    }
    

    func uploadLocalDataToCloud(completion: ((StorageMetadata?, Error?) -> Void)?) {
        let container = TarContainer.create(from: files)
        let fileType = StorageMetadata()
        
        let storageRef = Storage.storage().reference().child(UploadManager.rootFolder).child(Auth.auth().currentUser!.uid).child("\(UUID().uuidString).tar")
        
        fileType.contentType = "application/x-tar"
        let _ = storageRef.putData(container, metadata: fileType)
    }
    
    // downloads a file from filebase and writes into a temporary location
    func downloadFile(filePath: String) async -> URL? {
        let writeLocation: URL = NSURL.fileURL(withPathComponents: [NSTemporaryDirectory(), NSUUID().uuidString])!
        let storageRef = Storage.storage().reference().child(UploadManager.rootFolder).child(filePath)
        
        let localLocation: URL? = await withCheckedContinuation { continuation in
            
            storageRef.getData(maxSize: 1024*1024*1024) { (data: Data?, error: Error?) in
                guard let data = data else {
                    continuation.resume(returning: nil)
                    return
                }
                guard (try? data.write(to: writeLocation)) != nil else {
                    continuation.resume(returning: nil)
                    return
                }
                continuation.resume(returning: writeLocation)
                
            }
        }
        return localLocation
    }
   
}
